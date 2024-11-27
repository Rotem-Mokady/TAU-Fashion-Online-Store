import pandas as pd

from db_utils import fetch_data_from_mysql


def _get_available_cloths() -> pd.DataFrame:
    """
    Returns all available cloths.
    """
    query = """
    select  c.id, 
		    c.name,
            c.sex,
            c.price,
            c.inventory
        
    from taufashion_10.cloths c
    
    where c.inventory > 0
    
    order by c.campaign desc 
    """
    df = fetch_data_from_mysql(sql_statement=query)

    return df


def cloth_html_convertor() -> str:
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


