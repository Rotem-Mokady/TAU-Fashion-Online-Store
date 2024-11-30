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
        self.request_data = request_data
        self.current_table = current_table

    @staticmethod
    def _comparison_handler(old_val: Any, new_val: Any, key: str) -> Union[Any, None]:
        """
        New value for exists difference, None otherwise.
        """
        if key in ('Id', 'Inventory'):
            new_val = int(new_val)
        elif key == 'Price':
            new_val = float(new_val)
        elif key == 'Campaign':
            new_val = 1 if strtobool(new_val) else 0

        if old_val != new_val:
            return new_val

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
        new_values_updated_flag = False
        # iterate each row of the old data
        for current_row in self.current_table:
            product_id = current_row['Id']

            # on each row, check if the new values are different
            for key, val in current_row.items():
                request_key = f'{key}_{product_id}'
                new_value = self.request_data.get(request_key, default=val)

                # update only when new value actually exists
                new_value_to_update = self._comparison_handler(old_val=val, new_val=new_value, key=key)
                if new_value_to_update:
                    self._update_on_db(product_id=product_id, column_name=key, new_value=new_value_to_update)

                    # approve that at least one action has been done
                    if not new_values_updated_flag:
                        new_values_updated_flag = True

        return new_values_updated_flag






