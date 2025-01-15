from distutils.util import strtobool
from typing import Dict, List, Any

import pandas as pd

from db_utils import run_sql_command, push_dataframe_to_mysql, Tables


class _ParseRequestData:

    def __init__(self, request_data: Dict) -> None:
        """
        The table from the HTML sends in a different format.
        Parse it to the same structure of Cloths table.
        """
        self._request_data = request_data

        self._results = []
        self._current_row = {}

    def _current_row_insertion(self, param: str, value: str, familiar_flag: bool = True) -> None:
        # add param's name and it's value to the current row that the object is handling
        self._current_row[param] = value
        # each row includes exactly 7 parameters
        if len(self._current_row) == 7:
            # add old/new product flag, add the row to final results and create new empty row
            self._current_row['is_familiar'] = int(familiar_flag)
            self._results.append(self._current_row)
            self._current_row = {}

    def _parse_request(self) -> List[Dict]:
        # iterate each key and value from user request
        for key, val in self._request_data.items():

            # handle familiar products
            if not key.startswith('new_'):
                param, _ = key.split('_')
                self._current_row_insertion(param=param, value=val, familiar_flag=True)

            # handle the new product row
            else:
                _, param = key.split('_')
                self._current_row_insertion(param=param, value=val, familiar_flag=False)

        # save final results and "clean" the instance's variable itself
        results = self._results
        self._results = []

        return results

    @staticmethod
    def _data_prep_request_data_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data after the structure has been changed.
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

    def user_request_parser(self) -> pd.DataFrame:
        results = self._parse_request()
        df = pd.DataFrame(results)
        prepared_data = self._data_prep_request_data_df(df=df)

        return prepared_data


class UpdateClothsTable(_ParseRequestData):
    def __init__(self, request_data: Dict, current_table: List[Dict[str, Any]]) -> None:
        """
        Handle the updating of the Cloths table by the new table from Admins' Flask route.
        """
        super().__init__(request_data=request_data)

        self.current_table_df = pd.DataFrame(current_table)
        self.request_data_df = self.user_request_parser()

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

    @staticmethod
    def _merged_df_data_prep(df: pd.DataFrame) -> pd.DataFrame:
        # generate mask for finding changes between the two datasets and create a new filtered dataset
        different_product_mask = (
                (df['Name_old'] != df['Name_new']) |
                (df['Sex_old'] != df['Sex_new']) |
                (df['Path_old'] != df['Path_new']) |
                (df['Price_old'] != df['Price_new']) |
                (df['Inventory_old'] != df['Inventory_new']) |
                (df['Campaign_old'] != df['Campaign_new'])
        )
        filtered_df = df[different_product_mask]

        # remove irrelevant fields and change to the names on the DB itself
        relevant_fields = [col for col in filtered_df.columns if not col.endswith('_old')]
        final_df = filtered_df[relevant_fields]
        final_df.columns = [col.replace('_new', '') for col in final_df.columns]

        return final_df

    def _old_products_db_insertion(self, products_df: pd.DataFrame) -> None:
        if products_df.empty:
            return
        # iterate each familiar product that has been changed by an admin
        for record in products_df.to_dict(orient='records'):
            # extract product id
            product_id = record['Id']

            # update the DB about each parameter of the product
            for column_name, new_value in record.items():
                self._update_on_db(product_id=product_id, column_name=column_name, new_value=new_value)

    @staticmethod
    def _new_products_db_insertion(products_df: pd.DataFrame) -> None:
        # push all new products to DB (if there are)
        if not products_df.empty:
            push_dataframe_to_mysql(df=products_df, table_name=Tables.CLOTHS)

    def run(self) -> bool:
        """
        Returns True if one value or more have been updated, False otherwise.
        """
        # merge between the new data to the old, when the new is the "stronger" table
        merged_df = self.request_data_df.merge(
            self.current_table_df, how='left', on='Id', suffixes=('_new', '_old')
        )
        # data cleaning
        df_to_push = self._merged_df_data_prep(df=merged_df)

        # divide to two different datasets, one for UPDATE and another one for INSERT operations
        is_familiar_mask = df_to_push['is_familiar'] == 1
        familiar_products_df = df_to_push[is_familiar_mask].drop('is_familiar', axis=1)
        unfamiliar_products_df = df_to_push[~is_familiar_mask].drop('is_familiar', axis=1)

        # insert data to db
        self._old_products_db_insertion(products_df=familiar_products_df)
        self._new_products_db_insertion(products_df=unfamiliar_products_df)

        # if there was data to update/insert return True, otherwise False
        return not df_to_push.empty
