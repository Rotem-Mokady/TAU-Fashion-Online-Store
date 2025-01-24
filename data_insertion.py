import os
import pandas as pd

from utils.db_utils import run_sql_command, push_dataframe_to_mysql, Tables, ConnectionDetails, create_database


def create_tables() -> None:
    # ensure database exists
    create_database(db_name=ConnectionDetails.DB)

    # define dlls base dir
    base_dir = "sql\\dll"

    # iterate dlls and create table from each one
    for filename in os.listdir(base_dir):
        file_path = f'{base_dir}\\{filename}'
        with open(file_path, 'r', encoding='utf-8') as file:
            dll = file.read()
            sql_command = f'use {ConnectionDetails.DB};{dll}'
            run_sql_command(sql_command=sql_command)


def insert_data_to_db() -> None:
    """
    read the data of each target table and insert it to the DB
    """
    # define datasets base dir
    base_dir = "data_creation\\data"

    # create mapping between table to it's appropriate dataset
    table_to_xlsx_filename = {
        Tables.USERS: "users",
        Tables.CLOTHS: "cloths",
        Tables.TRANSACTIONS: "transactions",
        Tables.ITEMS: "transaction_to_items"
    }

    # push each datasets to the relevant target table
    for table_name, filename in table_to_xlsx_filename.items():
        file_path = f'{base_dir}\\{filename}.xlsx'
        df = pd.read_excel(file_path)
        push_dataframe_to_mysql(df=df, table_name=table_name)


def run() -> None:
    create_tables()
    insert_data_to_db()


if __name__ == '__main__':
    run()
