import pandas as pd

from utils.db_utils import push_dataframe_to_mysql, Tables


def run() -> None:
    base_dir = "data_creation\\data"
    table_to_xlsx_filename = {
        Tables.USERS: "users",
        Tables.CLOTHS: "cloths",
        Tables.TRANSACTIONS: "transactions",
        Tables.ITEMS: "transaction_to_items"
    }

    for table_name, filename in table_to_xlsx_filename.items():
        file_path = f'{base_dir}\\{filename}.xlsx'
        df = pd.read_excel(file_path)
        push_dataframe_to_mysql(df=df, table_name=table_name)


if __name__ == '__main__':
    run()
