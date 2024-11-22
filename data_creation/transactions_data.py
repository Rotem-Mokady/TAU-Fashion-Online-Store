import random
from typing import List, Dict, Any
import datetime as dt
import pandas as pd
from copy import deepcopy

from data_creation.data_generation_helpers import get_unique_column_values, get_random_time_within_range


class TransactionsGenerator:

    def __init__(self, orders_num: int) -> None:
        self.orders_num = orders_num

        self.emails = self._get_all_users_emails()
        self.cloths_ids = self._get_all_cloths_ids()

        self.start_date, self.end_date = dt.datetime(2024, 1, 1), dt.datetime(2024, 12, 31)
        self.start_hour, self.end_hour = 9, 19

        self.min_amount_of_products_in_order, self.max_amount_of_products_in_order = 1, 5


    @staticmethod
    def _get_all_users_emails() -> List[str]:
        """
        :return: list. All users in one list.
        """
        emails = get_unique_column_values(file_path="data\\users.xlsx", column_name='email')
        return emails

    @staticmethod
    def _get_all_cloths_ids() -> List[int]:
        """
        :return: list. All cloths ids in one list.
        """
        cloths_ids = get_unique_column_values(file_path="data\\cloths.xlsx", column_name='id')
        return cloths_ids

    @staticmethod
    def _generate_random_amount() -> int:
        """
        generate random amount of specific cloth in one order (between 1 and 20).
        :return: int.
        """
        return random.randint(1, 20)

    def _generate_random_time(self) -> dt.datetime:
        """
        generate random time between two dates and only between the opening hours of the store.
        :return: datetime object.
        """
        random_time = get_random_time_within_range(
            start_time=self.start_date, end_time=self.end_date, start_hour=self.start_hour, end_hour=self.end_hour
        )
        return random_time

    @staticmethod
    def _create_order_id(email: str, purchase_time: dt.datetime) -> int:
        """
        generate unique order id, based on user's email and the time of his order.
        :param email: str.
        :param purchase_time: datetime.
        :return: int. Unique order id.
        """
        # combine the two words into a single string
        combined = email + purchase_time.strftime('%d/%m/%Y %H:%M:%S')
        # use the hash function to create a hash value
        hashed_value = abs(hash(combined))

        return hashed_value

    def _generate_order(self) -> List[Dict[str, Any]]:
        """
        :return: list. An example an order.
        """
        # set all relevant details to create an order
        email, purchase_time = random.choice(self.emails), self._generate_random_time()
        order_id = self._create_order_id(email=email, purchase_time=purchase_time)

        # set the number of products in order
        transactions_num = random.randint(self.min_amount_of_products_in_order, self.max_amount_of_products_in_order)

        cloth_ids = deepcopy(self.cloths_ids)
        all_transactions_in_order = []

        for _ in range(transactions_num):
            # choose a random cloth id and remove it from the list of all
            cloth_id_random_index = random.randint(0, len(cloth_ids) - 1)
            chosen_cloth_id = cloth_ids.pop(cloth_id_random_index)

            # create transaction and insert it to the order list
            transaction = {
                'id': order_id,
                'user_mail': email,
                'cloth_id': chosen_cloth_id,
                'amount': self._generate_random_amount(),
                'purchase_time': purchase_time
            }
            all_transactions_in_order.append(transaction)

        return all_transactions_in_order

    def generate_orders(self) -> pd.DataFrame:
        """
        generate random orders.

        :return: pd.DataFrame.
        """
        orders = []
        for _ in range(self.orders_num):
            order = self._generate_order()
            orders += order

        return pd.DataFrame(orders)







