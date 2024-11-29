import pandas as pd

from db_utils import fetch_data_from_mysql


IMAGES_DIR = "static\\images\\products"


def _get_available_cloths() -> pd.DataFrame:
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

    df['path'] = df['path'].apply(lambda path: f"{IMAGES_DIR}\\{path}.jpeg")

    return df


def home_page_handler() -> str:
    """
    convert cloth DataFrame to HTML string.
    """
    df = _get_available_cloths()
    # capitalize columns names
    df.columns = [column.capitalize() for column in df.columns]
    # add user amount choosing column
    df['Your Order'] = 0
    # HTML table with classes for styling
    df_html = df.to_html(classes='table table-bordered table-striped', index=False)

    return df_html


