import random
import string
from typing import Dict, Any
import pandas as pd


COLORS = ['red', 'blue', 'green', 'black', 'white', 'yellow', 'purple', 'pink', 'grey', 'brown']
SEX = ['Men', 'Women']
CLOTHING_TYPES = ['shirt', 'pants']


def _generate_random_id() -> int:
    """
    :return: int. Random 8-digit id.
    """
    return int(''.join(random.choices(string.digits, k=8)))


def _generate_random_color() -> str:
    """
    :return: str. A random color from close list.
    """
    return random.choice(COLORS)


def _generate_sex() -> str:
    """
    :return: str. Randomly pick sex.
    """
    return random.choice(SEX)


def _generate_random_price() -> int:
    """
    Generate random price (between 100 and 1000)
    :return: str.
    """
    return random.randint(100, 1000)


def _generate_random_inventory() -> int:
    """
    generate random inventory (between 0 and 500)
    :return:
    """
    return random.randint(0, 500)


def _generate_campaign_flag() -> bool:
    """
    generate random campaign flag.
    :return: bool.
    """
    return random.choice([True, False])


def _generate_cloth_data() -> Dict[str, Any]:
    """
    Generate all the relevant data for one cloth.
    :return: dict.
    """
    _id = _generate_random_id()
    sex = _generate_sex()

    color, clothing_type = _generate_random_color(), random.choice(CLOTHING_TYPES)
    name = f"{color} {clothing_type}"

    data = {
        'id': _id,
        'name': name,
        'sex': sex,
        'campaign': _generate_campaign_flag(),
        'price': _generate_random_price(),
        'inventory': _generate_random_inventory(),
        'path': f"{sex}\\{name}\\{_id}"
    }

    return data


def get_cloths_data() -> pd.DataFrame:
    """
    :return: pd.DataFrame. 30 examples of cloths.
    """
    return pd.DataFrame([_generate_cloth_data() for _ in range(30)])

