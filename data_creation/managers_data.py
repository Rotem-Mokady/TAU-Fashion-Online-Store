import pandas as pd

from data_creation.data_generation_helpers import generate_random_password, convert_to_datetime


def get_managers_data() -> pd.DataFrame:
    """
    Generate list of managers users.
    :return: pd.DataFrame.
    """
    return pd.DataFrame([
        {'email': 'rotemmokady@gmail.com', 'username': 'Rotem_Mokady', 'password': generate_random_password(),
         'is_manager': 1, 'gender': 'Male', 'birth_date': convert_to_datetime('18/11/2000'), 'faculty': 'Exact Science'},
        {'email': 'galamittai@gmail.com', 'username': 'Gal_Amittai', 'password': generate_random_password(),
         'is_manager': 1, 'gender': 'Female', 'birth_date': convert_to_datetime('24/07/2001'), 'faculty': 'Exact Science'},
        {'email': 'asafbiran@gmail.com', 'username': 'Asaf_Biran', 'password': generate_random_password(),
         'is_manager': 1, 'gender': 'Male', 'birth_date': convert_to_datetime('29/06/1997'), 'faculty': 'Exact Science'}
    ])

