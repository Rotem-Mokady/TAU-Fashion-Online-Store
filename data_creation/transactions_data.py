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
        emails = get_unique_column_values(file_path="data_creation\\data\\users.xlsx", column_name='email')
        return emails

    @staticmethod
    def _get_all_cloths_ids() -> List[int]:
        """
        :return: list. All cloths ids in one list.
        """
        cloths_ids = get_unique_column_values(file_path="data_creation\\data\\cloths.xlsx", column_name='id')
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

    def _generate_transaction(self) -> Dict[str, Any]:
        """
        generate transaction with random email address and random times.
        :return: dict.
        """
        return {
            'user_mail': random.choice(self.emails),
            'purchase_time': self._generate_random_time()
        }

    def _get_transactions(self) -> pd.DataFrame:
        """
        generate transactions and give a unique id for each.
        :return: pd.Dataframe.
        """
        df = pd.DataFrame([self._generate_transaction() for _ in range(self.orders_num)])
        # sort the data according to the time
        sorted_df = df.sort_values('purchase_time', ascending=True).reset_index(drop=True)

        # add transaction id
        sorted_df.index.name = 'id'
        final_df = sorted_df.reset_index(drop=False)
        # start from 1
        final_df['id'] = final_df['id'].apply(lambda x: x + 1)

        return final_df

    def _generate_item_in_transaction(self, transaction_id: int, cloth_id: int) -> Dict[str, Any]:
        """
        generate product that ordered in specific transaction with an amount.
        :return: dict.
        """
        return {
            'transaction_id': transaction_id,
            'cloth_id': cloth_id,
            'amount': self._generate_random_amount()
        }

    def main(self) -> Dict[str, pd.DataFrame]:
        """
        generate random orders.

        :return: pd.DataFrame.
        """
        # transactions data
        transactions_df = self._get_transactions()

        items_data = []
        # create an actual order for each transaction
        for transaction_id in transactions_df['id']:

            # set the number of products in order
            items_num = random.randint(self.min_amount_of_products_in_order, self.max_amount_of_products_in_order)
            # get a list of all available products
            cloth_ids = deepcopy(self.cloths_ids)

            for _ in range(items_num):
                # choose a random cloth id and remove it from the list of all
                cloth_id_random_index = random.randint(0, len(cloth_ids) - 1)
                chosen_cloth_id = cloth_ids.pop(cloth_id_random_index)

                # add to the full list
                item_in_transaction = self._generate_item_in_transaction(
                    transaction_id=transaction_id, cloth_id=chosen_cloth_id
                )
                items_data.append(item_in_transaction)

        # items data
        items_df = pd.DataFrame(items_data)

        return {
            'transaction_data': transactions_df,
            'items_data': items_df
        }







