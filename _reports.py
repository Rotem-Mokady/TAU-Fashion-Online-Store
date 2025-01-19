import os
import pandas as pd

from utils.db_utils import fetch_data_from_mysql


def read_sql_files_in_directory(directory_path):
    statements = {}

    # Check if the provided directory exists
    if not os.path.isdir(directory_path):
        raise FileNotFoundError(f"The directory {directory_path} does not exist.")

    # Loop through the files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        query_name = filename.split('.')[0]

        # Only process .sql files
        if filename.endswith(".sql") and os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                statements[query_name] = file.read()

    return statements


def get_results():
    queries = read_sql_files_in_directory(directory_path='sql/reports')
    results = {}

    for query_name, sql in queries.items():
        results[query_name] = fetch_data_from_mysql(sql_statement=sql)

    return results


def main():
    results = get_results()

    with pd.ExcelWriter('reports_result.xlsx') as writer:
        for sheet_name, df in results.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


if __name__ == '__main__':
    main()
    print("*")
