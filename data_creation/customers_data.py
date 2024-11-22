import random
import pandas as pd

from data_creation.data_generation_helpers import generate_random_password, convert_to_datetime

FACULTIES = ['Engineering', 'Laws', 'Med']


def _assign_random_faculty() -> str:
    """
    Randomly assign a faculty.
    :return: str.
    """
    return random.choice(FACULTIES)


def get_regular_users_data() -> pd.DataFrame:
    """
    Generate list of regular users.
    :return: pd.DataFrame
    """
    return pd.DataFrame([
        {'email': 'beyonce@gmail.com', 'username': 'Beyonce', 'password': generate_random_password(), 'is_manager': 0, 'gender': 'Female', 'birth_date': convert_to_datetime('04/09/1981'), 'faculty': _assign_random_faculty()},
        {'email': 'justinbieber@gmail.com', 'username': 'Justin_Bieber', 'password': generate_random_password(), 'is_manager': 0, 'gender': 'Male', 'birth_date': convert_to_datetime('01/03/1994'), 'faculty': _assign_random_faculty()},
        {'email': 'katyperry@gmail.com', 'username': 'Katy_Perry', 'password': generate_random_password(), 'is_manager': 0, 'gender': 'Female', 'birth_date': convert_to_datetime('25/10/1984'), 'faculty': _assign_random_faculty()},
        {'email': 'taylorswift@gmail.com', 'username': 'Taylor_Swift', 'password': generate_random_password(), 'is_manager': 0, 'gender': 'Female', 'birth_date': convert_to_datetime('13/12/1989'), 'faculty': _assign_random_faculty()},
        {'email': 'edsheeran@gmail.com', 'username': 'Ed_Sheeran', 'password': generate_random_password(), 'is_manager': 0, 'gender': 'Male', 'birth_date': convert_to_datetime('17/02/1991'), 'faculty': _assign_random_faculty()},
        {'email': 'ariana_grande@gmail.com', 'username': 'Ariana_Grande', 'password': generate_random_password(), 'is_manager': 0, 'gender': 'Female', 'birth_date': convert_to_datetime('26/06/1993'), 'faculty': _assign_random_faculty()},
        {'email': 'drake@gmail.com', 'username': 'Drake', 'password': generate_random_password(), 'is_manager': 0, 'gender': 'Male', 'birth_date': convert_to_datetime('24/10/1986'), 'faculty': _assign_random_faculty()},
        {'email': 'billieeilish@gmail.com', 'username': 'Billie_Eilish', 'password': generate_random_password(), 'is_manager': 0, 'gender': 'Female', 'birth_date': convert_to_datetime('18/12/2001'), 'faculty': _assign_random_faculty()},
        {'email': 'ladygaga@gmail.com', 'username': 'Lady_Gaga', 'password': generate_random_password(), 'is_manager': 0, 'gender': 'Female', 'birth_date': convert_to_datetime('28/03/1986'), 'faculty': _assign_random_faculty()},
    ])
