import random
import string
import datetime as dt
import pandas as pd
from typing import List, Any, Union

from db_utils import push_dataframe_to_mysql


def get_unique_column_values(file_path: str, column_name: str) -> List[Any]:
    """
    get unique values from a specified column in an Excel file.
    Parameters:
    - file_path: str, path to the Excel file.
    - column_name: str, the name of the column to extract unique values from.

    Returns:
    - A list of unique values in the specified column.
    """
    df = pd.read_excel(file_path)
    unique_values = df[column_name].unique()

    return unique_values.tolist()


def generate_random_password() -> str:
    """
    Generate a random password.
    :return: str.
    """
    password_length = random.randint(8, 12)
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=password_length))
    return password


def convert_to_datetime(date_str: str) -> dt.datetime:
    """
    Convert date string to datetime object.
    :param date_str: str.
    :return: datetime.
    """
    return dt.datetime.strptime(date_str, '%d/%m/%Y')


def get_random_time_within_range(
        start_time: dt.date, end_time: dt.date, start_hour: int, end_hour: int
) -> Union[dt.datetime, dt.date]:
    """
    Returns a random time between two given times, restricted to between hours range.

    Parameters:
    - start_time: datetime object.
    - end_time: datetime object.
    - start_hour: int.
    - end_hour: int.

    Returns:
    - A random time between the specified times, restricted between hours range.
    """
    delta_days = (end_time - start_time).days

    random_days_delta = random.randint(0, delta_days)
    random_date = start_time + dt.timedelta(days=random_days_delta)

    random_hour = random.randint(start_hour, end_hour)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)

    time_to_add = dt.timedelta(hours=random_hour, minutes=random_minute, seconds=random_second)
    random_time = random_date + time_to_add

    return random_time


class PushToSql:
    """
    Object that push dataframe object to MySQL table.
    """
    def __init__(self, df: pd.DataFrame, table_name: str) -> None:
        """
        general params definitions.
        """
        self.df = df
        self.table_name = table_name

        self._local_data_path = ".\\data_creation\\data"

    def run(self, debug_mode: bool = True, to_excel: bool = False) -> None:
        # save data in Excel file if needed
        if to_excel:
            filename = f"{self._local_data_path}\\{self.table_name}.xlsx"
            self.df.to_excel(filename, index=False)

        # insert data only when debug mode if off
        if not debug_mode:
            push_dataframe_to_mysql(df=self.df, table_name=self.table_name)



