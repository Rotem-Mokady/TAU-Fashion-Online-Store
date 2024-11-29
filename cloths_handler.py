import pandas as pd
from typing import Dict, Any

from db_utils import fetch_data_from_mysql


class ClothsHandler:

    def __init__(self):

        self._images_dir = "static\\images\\products"

        self.home_page_df = self._home_page_handler()
        self.home_page_data_to_html = self.home_page_df.to_dict(orient='records')

    def _get_available_cloths(self) -> pd.DataFrame:
        """
        Returns all available cloths.
        """
        query = f"""
        select  c.id, 
                c.name,
                c.sex,
                c.price,
                c.inventory,
                replace(c.path, '\\\\', '\\\\\\\\') as path
            
        from taufashion_10.cloths c
        
        where c.inventory > 0
        
        order by c.campaign desc 
        """
        df = fetch_data_from_mysql(sql_statement=query)

        df['path'] = df['path'].apply(lambda path: f"{self._images_dir}\\{path}.jpeg")

        return df

    def _home_page_handler(self) -> pd.DataFrame:
        """
        convert cloth DataFrame to the Jinga handler.
        """
        df = self._get_available_cloths()
        # capitalize columns names
        df.columns = [column.capitalize() for column in df.columns]
        # add user amount choosing column
        df['Your Order'] = 0

        return df


def get_cloth_full_details(product_id: int, cloth_table: Dict[str, Any]) -> Dict[str, Any]:
    df = pd.DataFrame(cloth_table)
    mask = df['Id'] == product_id
    filtered_data = df[mask].to_dict(orient='records')

    if len(filtered_data) != 1:
        raise RuntimeError()

    data = filtered_data[0]
    return data


def generate_summary_info(product_info: Dict[str, Any], amount: int) -> Dict[str, Any]:
    final_info = {}
    for key, val in product_info.items():
        if key not in ('Inventory', 'Path', 'Your Order'):
            final_info[key] = val

    final_info['Total Amount'] = amount
    final_info['Total Price'] = amount * product_info['Price']

    return final_info


