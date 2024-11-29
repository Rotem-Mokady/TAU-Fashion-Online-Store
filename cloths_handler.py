import pandas as pd

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


