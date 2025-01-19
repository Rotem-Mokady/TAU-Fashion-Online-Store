import pandas as pd

from utils.db_utils import fetch_data_from_mysql


class ClothsSqlStatements:

    @property
    def admins_query(self) -> str:
        # parse path field to avoid slashed issues
        return """
            SELECT  c.id, 
                    c.name,
                    replace(c.path, '\\\\', '\\\\\\\\') as path,
                    c.price,
                    c.inventory,
                    c.campaign
            
            FROM taufashion_10.cloths c
            
            -- show first all the products that had a campaign
            ORDER BY c.campaign desc
        """

    @property
    def costumers_query(self) -> str:
        # parse path field to avoid slashed issues
        return """
            SELECT  c.id, 
                    c.name,
                    c.price,
                    c.inventory,
                    replace(c.path, '\\\\', '\\\\\\\\') as path
                
            FROM taufashion_10.cloths c
            
            -- products outside of inventory are irrelevant
            WHERE c.inventory > 0
            
            -- show first all the products that had a campaign
            ORDER BY c.campaign desc 
        """


class ClothsDataCollection(ClothsSqlStatements):

    def __init__(self) -> None:
        """
        General object to deal with data transformations from the DB to 'home_page' and 'admin' Flask app routes.
        """
        super().__init__()
        # the local path of all cloths' images
        self._images_dir = "../static/images/products"

        # get different dataframes for each Flask route, create also a version for advanced HTML manipulations (Jinja).

        self.home_page_df = self._home_page_handler()
        self.home_page_data_to_html = self.home_page_df.to_dict(orient='records')

        self.admin_page_df = self._admin_page_handler()
        self.admin_page_data_to_html = self.admin_page_df.to_dict(orient='records')

    def _admin_page_handler(self) -> pd.DataFrame:
        """
        Prepare general dataframe for Admin's Flask route.
        """
        # get raw data
        df = fetch_data_from_mysql(sql_statement=self.admins_query)
        # capitalize columns names
        df.columns = [column.capitalize() for column in df.columns]

        return df

    def _home_page_handler(self) -> pd.DataFrame:
        """
        Prepare general dataframe for Home Page Flask route.
        """
        # get raw data
        df = fetch_data_from_mysql(sql_statement=self.costumers_query)
        # make 'Path' field a full path, for next href using on the HTML template
        df['path'] = df['path'].apply(lambda path: f"{self._images_dir}\\{path}.jpeg")

        # capitalize columns names
        df.columns = [column.capitalize() for column in df.columns]
        # add user amount choosing column
        df['Your Order'] = 0

        return df





