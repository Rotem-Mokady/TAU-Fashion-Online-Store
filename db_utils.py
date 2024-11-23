import socket
import pandas as pd
from typing import Union
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import SQLAlchemyError


def _get_ip_address() -> str:
    """
    Find IP address for the connection to MySQL database.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    # some IP address that's guaranteed to be reachable
    s.connect(('1.1.1.1', 1))

    # get the IP address and close the socket session
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address


class ConnectionDetails:
    USERNAME = 'root'
    PASSWORD = 'root'
    IP_ADDRESS = _get_ip_address()
    DB = 'taufashion_10'


class Tables:
    USERS = "users"
    CLOTHS = "cloths"
    TRANSACTIONS = "transactions"


def create_mysql_engine() -> Engine:
    """
    :return: general MySQL engine to TAUFashion's schema.
    """
    connection_string = f"" \
                        f"mysql+mysqlconnector://{ConnectionDetails.USERNAME}:{ConnectionDetails.PASSWORD}@" \
                        f"{ConnectionDetails.IP_ADDRESS}/{ConnectionDetails.DB}"
    engine = create_engine(connection_string)

    return engine


def fetch_data_from_mysql(sql_statement: str) -> Union[pd.DataFrame, None]:
    """
    The function returns SQL query output as Pandas Dataframe object.

    :param sql_statement: str.
    :return: pd.DataFrame.
    """
    try:
        engine = create_mysql_engine()
        df = pd.read_sql(sql_statement, engine)

        return df

    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None


def push_dataframe_to_mysql(
        df: pd.DataFrame, table_name: str, if_exists='append'
) -> None:
    """
    Pushes a pandas DataFrame to a MySQL table.

    Parameters:
    - df: pandas DataFrame.
    - table_name: str, name of the MySQL table.
    - if_exists: str, behavior when the table already exists ('append', 'replace', 'fail').

    All technical details are already provided.
    """
    try:
        # Create a connection to the MySQL database
        engine = create_mysql_engine()

        # Push the dataframe to the table
        df.to_sql(name=table_name, con=engine, if_exists=if_exists, index=False)

        print(f"{len(df)} records successfully inserted into the {table_name} table.")

    except Exception as e:
        print(f"An error occurred: {e}")


def run_sql_command(sql_command: str) -> None:
    """
    The function gets a sql command line and run it via MySQL engine of TAUFashion.
    """
    try:
        # create a connection to the MySQL database
        engine = create_mysql_engine()
        # establish a connection to the database using the engine
        with engine.connect() as connection:
            # Execute the provided SQL command
            connection.execute(sql_command)
            connection.execute('commit;')
            print("SQL command executed successfully.")

    except SQLAlchemyError as e:
        print(f"Error executing SQL command: {e}")


# if __name__ == '__main__':
#     sql_command = "UPDATE taufashion_10.users SET password = 'Sj6mKQxM0fMr' WHERE username = 'Rotem_Mokady'"
#     run_sql_command(sql_command)

