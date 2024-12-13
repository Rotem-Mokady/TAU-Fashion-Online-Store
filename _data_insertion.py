import pandas as pd

from data_creation.data_generation_helpers import PushToSql

from data_creation.managers_data import get_managers_data
from data_creation.customers_data import get_regular_users_data
from data_creation.cloths_data import get_cloths_data
from data_creation.transactions_data import TransactionsGenerator
from db_utils import Tables


def users_data_handler() -> None:
    """
    handle users data.
    """
    managers_data, regular_users_data = get_managers_data(), get_regular_users_data()
    all_users_data = pd.concat([managers_data, regular_users_data], ignore_index=True)

    PushToSql(df=all_users_data, table_name=Tables.USERS).run(debug_mode=True, to_excel=False)


def cloths_data_handler() -> None:
    """
    handle cloths data.
    """
    data = get_cloths_data()

    PushToSql(df=data, table_name=Tables.CLOTHS).run(debug_mode=True, to_excel=False)


def transactions_data_handler() -> None:
    """
    handle transactions data.
    """
    data = TransactionsGenerator(orders_num=2000).generate_orders()

    PushToSql(df=data, table_name=Tables.TRANSACTIONS).run(debug_mode=True, to_excel=False)


if __name__ == '__main__':
    # users_data_handler()
    # cloths_data_handler()
    # transactions_data_handler()
    pass