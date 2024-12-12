from typing import Dict, Any
import re
import datetime as dt
import pandas as pd

from db_utils import fetch_data_from_mysql, push_dataframe_to_mysql, Tables


def signing_in_response(username: str, password: str) -> bool:
    """
    The function checks if the username and password are familiar or not, based on our store's DB.

    :param username: str.
    :param password: str.
    :return: bool. True if exists, False if not.
    """
    # create an appropriate SQL query and fetch the results from the DB
    statement = f"""
    SELECT *
    FROM taufashion_10.users u
    WHERE u.username = '{username}' AND u.password = '{password}'
    """
    df = fetch_data_from_mysql(sql_statement=statement)

    # False if the user is not familiar, True if he is
    # note that we expect only to one or zero records exactly
    if df.empty:
        return False
    elif len(df) == 1:
        return True
    else:
        raise RuntimeError()


def validate_email_template(email: str) -> bool:
    """
    correct email must to end with '.com' suffix, include '@' and start with a letter.

    :param email: str.
    :return: bool. True If email's template is correct, unless False.
    """
    return email.endswith('.com') and email.find('@') >= 0 and bool(re.match('[A-Za-z]', email))


def validate_username_template(username: str) -> bool:
    """
    correct username must be alphanumeric (letters, numbers) and between 8 to 20 characters.

    :param username: str.
    :return: bool. True If username's template is correct, unless False.
    """
    # if nothing extracted return False
    extraction = re.match('\w+', username)
    if not extraction:
        return False

    # return True only if the username is alphanumeric as it is and it's length in the defined range
    return username == extraction.group() and 8 <= len(username) <= 20


def validate_password_template(password: str) -> bool:
    """
    correct password must to be in length of 8 to 20 chars and with no spaces.

    :param password: str.
    :return: bool. True If password's template is correct, unless False.
    """
    return 8 <= len(password) <= 20 and password == password.replace(' ', '')


def ensure_new_user(email: str, username: str) -> bool:
    """
    Make sure that the email and the username do not already exist.

    :param email: str.
    :param username: str.
    :return:bool. True if they are new, otherwise False.
    """
    # create an appropriate SQL query and fetch the results from the DB
    statement = f"""
        SELECT *
        FROM taufashion_10.users u
        WHERE u.email = '{email}' OR u.username = '{username}' 
    """
    df = fetch_data_from_mysql(sql_statement=statement)

    # it's a new user if there are no results at all, otherwise it's an old one
    return df.empty


def ensure_minimum_age(birth_date_str: str) -> bool:
    """
    Make sure that the user is 18 years old at least.
    """
    # parse date string to date object
    birth_date = dt.datetime.strptime(birth_date_str, '%Y-%m-%d').date()
    # get current date
    current_date = dt.datetime.now().date()
    # compare between to dates
    years_diff = (current_date - birth_date).days / 365
    # True if the user is equal or greater than the minimum age, otherwise False
    return years_diff >= 18


def register_new_user(request_data: Dict[str, Any]) -> None:
    """
    Register a new user, after he passed all signing up validations.
    """
    # new user is always not an admin
    user_data = {'is_manager': False}

    # parse user's request parameters
    for key, val in request_data.items():
        if key == 'birth_date':
            user_data[key] = dt.datetime.strptime(val, '%Y-%m-%d')
        elif key != 'confirm_password':
            user_data[key] = val

    # insert new user's details to DB
    df = pd.DataFrame([user_data])
    push_dataframe_to_mysql(df=df, table_name=Tables.USERS)


def is_admin(username: str) -> bool:
    """
    :param username: str.
    :return: bool. True if the user is defined as admin, otherwise False.
    """
    # create an appropriate SQL query and fetch the results from the DB
    statement = f"""
            SELECT *
            FROM taufashion_10.users u
            WHERE u.username = '{username}' AND u.is_manager = 1
        """

    df = fetch_data_from_mysql(sql_statement=statement)

    # the user is a manager only if he has the appropriate flag in the DB, otherwise he is a regular user
    return not df.empty


def get_email_by_username(username: str) -> str:
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
