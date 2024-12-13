import datetime as dt
from typing import List, Dict, Any

import pandas as pd

from db_utils import push_dataframe_to_mysql, Tables, run_sql_command, fetch_data_from_mysql


def get_product_full_details(product_id: int, cloths_table: List[Dict[str, Any]]) -> Dict[str, Any]:
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


def _get_email_by_username(username: str) -> str:
    """
    :param username: str.
    :return: str. Email address.
    """
    # create an appropriate SQL query and fetch the results from the DB
    statement = f"""
        SELECT u.email
        FROM taufashion_10.users u
        WHERE u.username = '{username}'
    """
    df = fetch_data_from_mysql(sql_statement=statement)

    # note that we expect to only one record exactly
    if len(df) != 1:
        raise RuntimeError()

    # extract the email and return it
    email = df['email'][0]
    return email


def add_transaction_to_db(username: str, data: List[Dict[str, Any]]) -> None:
    """
    Add to the DB the new transactions of the user
    """
    # get email and the current time
    email = _get_email_by_username(username=username)
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
