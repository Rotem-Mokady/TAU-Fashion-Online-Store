import pandas as pd
import datetime as dt
from typing import List, Dict, Any, Union
from distutils.util import strtobool

from db_utils import fetch_data_from_mysql, push_dataframe_to_mysql, Tables, run_sql_command
from auth_and_register import get_email_by_username


class ClothsHandler:

    def __init__(self):

        self._images_dir = "static\\images\\products"

        self.home_page_df = self._home_page_handler()
        self.home_page_data_to_html = self.home_page_df.to_dict(orient='records')

        self.admin_page_df = self._admin_page_handler()
        self.admin_page_data_to_html = self.admin_page_df.to_dict(orient='records')

    @staticmethod
    def _collect_raw_data() -> pd.DataFrame:
        """
        Returns all the data as it is.
        """
        query = """
            select  c.id, 
                    c.name,
                    c.sex,
                    replace(c.path, '\\\\', '\\\\\\\\') as path,
                    c.price,
                    c.inventory,
                    c.campaign
            
            from taufashion_10.cloths c
            
            order by c.campaign desc
        """
        df = fetch_data_from_mysql(sql_statement=query)

        return df

    def _admin_page_handler(self) -> pd.DataFrame:
        """
        convert cloths DataFrame to the Jinga handler.
        """
        df = self._collect_raw_data()
        # capitalize columns names
        df.columns = [column.capitalize() for column in df.columns]

        return df

    def _get_available_cloths_for_costumers(self) -> pd.DataFrame:
        """
        Returns all available cloths.
        """
        query = f"""
        select  c.id, 
                c.name,
                c.sex,
                c.price,
                c.inventory,
                replace(c.path, '\\\\', '\\\\\\\\') as path
            
        from taufashion_10.cloths c
        
        where c.inventory > 0
        
        order by c.campaign desc 
        """
        df = fetch_data_from_mysql(sql_statement=query)

        df['path'] = df['path'].apply(lambda path: f"{self._images_dir}\\{path}.jpeg")

        return df

    def _home_page_handler(self) -> pd.DataFrame:
        """
        convert cloths DataFrame to the Jinga handler.
        """
        df = self._get_available_cloths_for_costumers()
        # capitalize columns names
        df.columns = [column.capitalize() for column in df.columns]
        # add user amount choosing column
        df['Your Order'] = 0

        return df


def get_cloth_full_details(product_id: int, cloths_table: Dict[str, Any]) -> Dict[str, Any]:
    df = pd.DataFrame(cloths_table)
    mask = df['Id'] == product_id
    filtered_data = df[mask].to_dict(orient='records')

    if len(filtered_data) != 1:
        raise RuntimeError()

    data = filtered_data[0]
    return data


def generate_summary_info(product_info: Dict[str, Any], amount: int) -> Dict[str, Any]:
    final_info = {}
    for key, val in product_info.items():
        if key not in ('Inventory', 'Path', 'Your Order'):
            final_info[key] = val

    final_info['Total Amount'] = amount
    final_info['Total Price'] = amount * product_info['Price']

    return final_info


def add_transaction_to_db(username: str, data: List[Dict[str, Any]]) -> None:
    email = get_email_by_username(username=username)
    current_time = dt.datetime.now()

    email_and_time_unique_str = email + current_time.strftime('%d/%m/%Y %H:%M:%S')
    transaction_id = abs(hash(email_and_time_unique_str))

    data = [{
        'id': transaction_id,
        'user_mail': email,
        'cloth_id': cloth_data['Id'],
        'amount': cloth_data['Total Amount'],
        'purchase_time': current_time
    } for cloth_data in data]
    df = pd.DataFrame(data)

    push_dataframe_to_mysql(df=df, table_name=Tables.TRANSACTIONS)


class UpdateClothsTable:
    def __init__(self, request_data: Dict, current_table: List[Dict[str, Any]]) -> None:
        """
        Push new table from managers' page to cloth table.
        """
        self.current_table_df = pd.DataFrame(current_table)
        self.request_data_df = self._parse_request_data(request_data=request_data)

    @staticmethod
    def _parse_request_data(request_data: Dict) -> pd.DataFrame:
        results = []
        current_row = {}

        for key, val in request_data.items():
            param, _ = key.split('_')
            current_row[param] = val

            if len(current_row) == 7:
                results.append(current_row)
                current_row = {}

        df = pd.DataFrame(results)

        df['Id'] = df['Id'].astype('int64')
        df['Inventory'] = df['Inventory'].astype('int64')
        df['Price'] = df['Price'].astype(float)
        df['Campaign'] = df['Campaign'].apply(lambda x: 1 if strtobool(x) else 0)

        return df

    @staticmethod
    def _update_on_db(product_id: int, column_name: str, new_value: Any):
        new_value_sql = f"'{new_value}'" if isinstance(new_value, str) else new_value
        stm = f"""
            update cloths
            set {column_name.lower()} = {new_value_sql}
            where id = {product_id}
        """

        run_sql_command(sql_command=stm)

    def run(self) -> bool:
        """
        Returns True if one value or more have been updated, False otherwise.
        """
        df_of_all = self.request_data_df.merge(
            self.current_table_df, how='left', on='Id', suffixes=('_new', '_old')
        )

        different_product_mask = (
            (df_of_all['Name_old'] != df_of_all['Name_new']) |
            (df_of_all['Sex_old'] != df_of_all['Sex_new']) |
            (df_of_all['Path_old'] != df_of_all['Path_new']) |
            (df_of_all['Price_old'] != df_of_all['Price_new']) |
            (df_of_all['Inventory_old'] != df_of_all['Inventory_new']) |
            (df_of_all['Campaign_old'] != df_of_all['Campaign_new'])
        )
        filtered_df = df_of_all[different_product_mask]

        relevant_fields = [col for col in filtered_df.columns if not col.endswith('_old')]
        df_to_push = filtered_df[relevant_fields]
        df_to_push.columns = [col.split('_')[0] for col in df_to_push.columns]

        for record in df_to_push.to_dict(orient='records'):
            product_id = record['Id']

            for column_name, new_value in record.items():
                self._update_on_db(product_id=product_id, column_name=column_name, new_value=new_value)

        return not df_to_push.empty





