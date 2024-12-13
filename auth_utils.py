from db_utils import fetch_data_from_mysql


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