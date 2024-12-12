import pandas as pd
import datetime as dt
from typing import List, Dict, Any
from distutils.util import strtobool

from db_utils import fetch_data_from_mysql, push_dataframe_to_mysql, Tables, run_sql_command
from auth_and_register import get_email_by_username


class ClothsHandler:

    def __init__(self) -> None:
        """
        General object to deal with data transformations from the DB to 'home_page' and 'admin' Flask app routes.
        """
        # the local path of all cloths' images
        self._images_dir = "static\\images\\products"

        # get different dataframes for each Flask route, create also a version for advanced HTML manipulations (Jinja).

        self.home_page_df = self._home_page_handler()
        self.home_page_data_to_html = self.home_page_df.to_dict(orient='records')

        self.admin_page_df = self._admin_page_handler()
        self.admin_page_data_to_html = self.admin_page_df.to_dict(orient='records')

    @staticmethod
    def _collect_raw_data() -> pd.DataFrame:
        """
        Returns all raw data as it is.
        """
        # create an appropriate SQL query and fetch the results from the DB
        # parse path field to avoid slashed issues
        query = """
            SELECT  c.id, 
                    c.name,
                    c.sex,
                    replace(c.path, '\\\\', '\\\\\\\\') as path,
                    c.price,
                    c.inventory,
                    c.campaign
            
            FROM taufashion_10.cloths c
            
            -- show first all the products that had a campaign
            ORDER BY c.campaign desc
        """
        df = fetch_data_from_mysql(sql_statement=query)

        return df

    def _admin_page_handler(self) -> pd.DataFrame:
        """
        Prepare general dataframe for Admin's Flask route.
        """
        # get raw data
        df = self._collect_raw_data()
        # capitalize columns names
        df.columns = [column.capitalize() for column in df.columns]

        return df

    def _get_available_cloths_for_costumers(self) -> pd.DataFrame:
        """
        Returns all relevant data for costumers.
        """
        # create an appropriate SQL query and fetch the results from the DB
        # parse path field to avoid slashed issues
        query = f"""
        SELECT  c.id, 
                c.name,
                c.sex,
                c.price,
                c.inventory,
                replace(c.path, '\\\\', '\\\\\\\\') as path
            
        FROM taufashion_10.cloths c
        
        -- products outside of inventory are irrelevant
        WHERE c.inventory > 0
        
        -- show first all the products that had a campaign
        ORDER BY c.campaign desc 
        """
        df = fetch_data_from_mysql(sql_statement=query)

        # make 'Path' field a full path, for next href using on the HTML template
        df['path'] = df['path'].apply(lambda path: f"{self._images_dir}\\{path}.jpeg")

        return df

    def _home_page_handler(self) -> pd.DataFrame:
        """
        Prepare general dataframe for Home Page Flask route.
        """
        df = self._get_available_cloths_for_costumers()
        # capitalize columns names
        df.columns = [column.capitalize() for column in df.columns]
        # add user amount choosing column
        df['Your Order'] = 0

        return df


def get_cloth_full_details(product_id: int, cloths_table: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract all saved data about the product id from cloth table
    """
    # convert array to DataFrame and filter on the given product
    df = pd.DataFrame(cloths_table)
    mask = df['Id'] == product_id
    filtered_data = df[mask].to_dict(orient='records')

    # note that we expect to one record exactly
    if len(filtered_data) != 1:
        raise RuntimeError()

    # send the results as dictionary of the product
    data = filtered_data[0]
    return data


def generate_summary_info(product_info: Dict[str, Any], amount: int) -> Dict[str, Any]:
    """
    Generate advanced summary info, based on the given product's details and the amount of it in the total order.
    """
    # filter out all irrelevant details
    final_info = {}
    for key, val in product_info.items():
        if key not in ('Inventory', 'Path', 'Your Order'):
            final_info[key] = val

    # add an amount
    final_info['Total Amount'] = amount
    # calculate total price for this product
    final_info['Total Price'] = amount * product_info['Price']

    return final_info


def add_transaction_to_db(username: str, data: List[Dict[str, Any]]) -> None:
    """
    Add to the DB the new transactions of the user
    """
    # get email and the current time
    email = get_email_by_username(username=username)
    current_time = dt.datetime.now()

    # generate an unique id for the order
    email_and_time_unique_str = email + current_time.strftime('%d/%m/%Y %H:%M:%S')
    transaction_id = abs(hash(email_and_time_unique_str))

    # generate all the records of the order
    data = [{
        'id': transaction_id,
        'user_mail': email,
        'cloth_id': cloth_data['Id'],
        'amount': cloth_data['Total Amount'],
        'purchase_time': current_time
    } for cloth_data in data]

    # convert to DataFrame and insert it to the DB
    df = pd.DataFrame(data)
    push_dataframe_to_mysql(df=df, table_name=Tables.TRANSACTIONS)


def update_products_inventory(transaction_data: List[Dict[str, Any]]) -> None:
    """
    Update the total inventory of all products in given order transaction.
    """
    # iterate each product in the order
    for cloth_data in transaction_data:
        # extract product id and the purchased amount
        product_id = cloth_data['Id']
        amount_to_subtract = cloth_data['Total Amount']

        # create an appropriate SQL statement that subtract the purchased amount from the total inventory
        update_stm = f"""
            UPDATE cloths
            SET inventory = inventory - {amount_to_subtract}
            WHERE id = {product_id}
        """
        # run SQL statement on the DB
        run_sql_command(sql_command=update_stm)


class UpdateClothsTable:
    def __init__(self, request_data: Dict, current_table: List[Dict[str, Any]]) -> None:
        """
        Handle the updating of the Cloths table by the new table from Admins' Flask route.
        """
        self.current_table_df = pd.DataFrame(current_table)
        self.request_data_df = self._parse_request_data(request_data=request_data)

    def _parse_request_data(self, request_data: Dict) -> pd.DataFrame:
        """
        The table from the HTML sends in a different format.
        Parse it to the same structure of Cloths table.
        """
        results = []
        current_row = {}

        for key, val in request_data.items():

            # handle familiar products
            if not key.startswith('new_'):
                param, _ = key.split('_')
                current_row[param] = val

                # each row includes exactly 7 parameters
                if len(current_row) == 7:
                    # add old product flag, add the row to final results and create new empty row
                    current_row['is_unfamiliar'] = 0
                    results.append(current_row)
                    current_row = {}

            # handle the new product row
            else:
                _, param = key.split('_')
                current_row[param] = val

                # each row includes exactly 7 parameters
                if len(current_row) == 7:
                    # add new product flag, add the row to final results and create new empty row
                    current_row['is_unfamiliar'] = 1
                    results.append(current_row)
                    current_row = {}

        # convert to df and clean the data
        df = pd.DataFrame(results)
        prepared_df = self._data_prep_request_data_df(df)

        return prepared_df

    @staticmethod
    def _data_prep_request_data_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data for updating
        """
        # remove duplications of IDs
        no_dup_df = df.drop_duplicates(subset='Id', keep='first')
        # remove rows with None (anywhere)
        df_cleaned = no_dup_df[~no_dup_df.isin([None, '']).any(axis=1)]

        # handle dtypes
        df_cleaned['Id'] = df_cleaned['Id'].astype('int64')
        df_cleaned['Inventory'] = df_cleaned['Inventory'].astype('int64')
        df_cleaned['Price'] = df_cleaned['Price'].astype(float)
        df_cleaned['Campaign'] = df_cleaned['Campaign'].apply(lambda x: 1 if strtobool(x) else 0)

        return df_cleaned

    @staticmethod
    def _update_on_db(product_id: int, column_name: str, new_value: Any) -> None:
        """
        Get product id, column name to update for the given product id and the new value to set.
        """
        # if it's a string field, parse it to SQL format
        new_value_sql = f"'{new_value}'" if isinstance(new_value, str) else new_value
        # generate SQL statement
        stm = f"""
            UPDATE cloths
            SET {column_name.lower()} = {new_value_sql}
            WHERE id = {product_id}
        """
        # run statement on DB
        run_sql_command(sql_command=stm)

    def run(self) -> bool:
        """
        Returns True if one value or more have been updated, False otherwise.
        """
        # merge between the new data to the old, when the new is the "stronger" table
        df_of_all = self.request_data_df.merge(
            self.current_table_df, how='left', on='Id', suffixes=('_new', '_old')
        )

        # generate mask for finding changes between the two datasets and create a new filtered dataset
        different_product_mask = (
            (df_of_all['Name_old'] != df_of_all['Name_new']) |
            (df_of_all['Sex_old'] != df_of_all['Sex_new']) |
            (df_of_all['Path_old'] != df_of_all['Path_new']) |
            (df_of_all['Price_old'] != df_of_all['Price_new']) |
            (df_of_all['Inventory_old'] != df_of_all['Inventory_new']) |
            (df_of_all['Campaign_old'] != df_of_all['Campaign_new'])
        )
        filtered_df = df_of_all[different_product_mask]

        # remove irrelevant fields and change to the names on the DB itself
        relevant_fields = [col for col in filtered_df.columns if not col.endswith('_old')]
        df_to_push = filtered_df[relevant_fields]
        df_to_push.columns = [col.replace('_new', '') for col in df_to_push.columns]

        # divide to two different datasets, one for UPDATE and another one for INSERT operations
        is_unfamiliar_mask = df_to_push['is_unfamiliar'] == 1
        unfamiliar_products_df = df_to_push[is_unfamiliar_mask].drop('is_unfamiliar', axis=1)
        familiar_products_df = df_to_push[~is_unfamiliar_mask].drop('is_unfamiliar', axis=1)

        # iterate each familiar product that has been changed by an admin
        for record in familiar_products_df.to_dict(orient='records'):
            # extract product id
            product_id = record['Id']

            # update the DB about each parameter of the product
            for column_name, new_value in record.items():
                self._update_on_db(product_id=product_id, column_name=column_name, new_value=new_value)

        # push all new products to DB (if there are)
        if not unfamiliar_products_df.empty:
            push_dataframe_to_mysql(df=unfamiliar_products_df, table_name=Tables.CLOTHS)

        # if there was data to update/insert return True, otherwise False
        return not df_to_push.empty





