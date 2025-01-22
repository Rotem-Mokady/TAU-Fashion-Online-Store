import os
from distutils.util import strtobool
from typing import Dict, List, Any, Tuple, Union

from werkzeug.datastructures import FileStorage
from PIL import Image
import pandas as pd

from utils.db_utils import run_sql_command, push_dataframe_to_mysql, Tables


def _convert_to_jpeg(image_path):
    """
    Converts the image at the given path to JPEG format, if it is not already JPEG.

    Parameters:
        image_path (str): Path to the image file to be checked and converted.

    Returns:
        str: Path to the saved JPEG image.
    """
    # Open the image
    with Image.open(image_path) as img:
        # Check the format of the image
        if img.format.lower() == 'jpeg':
            print(f"Image is already in JPEG format: {image_path}")
            return image_path  # No need to convert, return the original path

        # Convert the image to JPEG if it isn't already
        new_image_path = os.path.splitext(image_path)[0] + '.jpeg'  # Save with a .jpeg extension

        # Convert the image and save as JPEG
        img.convert('RGB').save(new_image_path, 'JPEG')  # Convert to RGB (necessary for non-RGB images like PNG)

        print(f"Image converted to JPEG and saved at: {new_image_path}")
        return new_image_path


class UpdateClothsTable:
    def __init__(
            self, request_data: Dict, current_table: List[Dict[str, Any]], new_image: Union[FileStorage, None]
    ) -> None:
        """
        Handle the updating of the Cloths table by the new table from Admins' Flask route.
        """
        self._current_table_df = pd.DataFrame(current_table)
        self._current_id_to_inventory = {
            row['Id']: row['Inventory'] for row in self._current_table_df.to_dict(orient='records')
        }

        self._familiar_products_inventory, self._new_product_row = self._parse_request_data(request_data=request_data)
        self._new_image = new_image
        self._new_image_existence = bool(self._new_image.filename)

        self._inventory_param_name = 'Inventory'
        self._images_target_path = 'static\\images\\products\\'

    @staticmethod
    def _parse_request_data(request_data: Dict) -> Tuple[Dict, Dict]:
        """
        parse data from HTML.
        """
        familiar_products_inventory, new_product_row = {}, {}
        for key, val in request_data.items():

            # handle familiar products
            if key.startswith('Inventory_'):
                _, product_id = key.split('_')
                familiar_products_inventory[int(product_id)] = int(val)

            # handle new product
            elif key.startswith('new_'):
                _, param_name = key.split('_')
                new_product_row[param_name] = val

            # any other case should not happen
            else:
                raise RuntimeError()

        return familiar_products_inventory, new_product_row

    @staticmethod
    def _update_on_db(product_id: int, column_name: str, new_value: Any) -> None:
        """
        Get product id, column name to update for the given product id and the new value to set.
        """
        # if it's a string field, parse it to SQL format
        new_value_sql = f"'{new_value}'" if isinstance(new_value, str) else new_value
        # generate SQL statement
        stm = f"""
            UPDATE cloths
            SET {column_name.lower()} = {new_value_sql}
            WHERE id = {product_id}
        """
        # run statement on DB
        run_sql_command(sql_command=stm)

    def _update_familiar_products(self) -> bool:
        """
        For each one of the familiar products, check if the user sent a different inventory from the current.
        Return True for at least one different inventory, otherwise False.
        """
        # set updating flag
        update_done = False

        # iterate the familiar products from user
        for product_id, new_inventory in self._familiar_products_inventory.items():
            # compare old to new
            old_inventory = self._current_id_to_inventory[product_id]
            if new_inventory != old_inventory:

                # update in case of difference, and change the updating flag if needed
                self._update_on_db(
                    product_id=product_id, column_name=self._inventory_param_name, new_value=new_inventory
                )
                if not update_done:
                    update_done = True

        return update_done

    def _upload_image(self) -> None:
        """
        Upload the image from the user to the appropriate local path
        """
        # do nothing if there is no file
        if not self._new_image_existence:
            return

        # generate full path
        file_extension = self._new_image.filename.split('.')[-1]
        image_path = f"{self._images_target_path}{self._new_product_row['Path']}.{file_extension}"
        # create dir if not exists
        dir_name = os.path.dirname(image_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        # save image and convert to jpeg if needed
        self._new_image.save(image_path)
        _convert_to_jpeg(image_path)

    def _insert_new_product(self) -> bool:
        """
        Add the new product if the inserted data is valid.
        Return True if the new record has been inserted, otherwise False
        """
        # do not insert without an image
        if not self._new_image_existence:
            return False

        final_record = {}
        # validate and parse each parameter
        for param, value in self._new_product_row.items():

            # if there is at least one empty value, do not insert
            if value == '':
                return False
            # if the id is already exists, do not insert
            elif param == 'Id' and value in self._current_id_to_inventory:
                return False

            # convert to int if needed
            elif param in ('Id', 'Inventory'):
                final_record[param] = int(value)
            # convert to float if needed
            elif param == 'Price':
                final_record[param] = float(value)
            # convert tp boolean if needed
            elif param == 'Campaign':
                final_record[param] = strtobool(value)
            # insert the value as it is
            else:
                final_record[param] = value

        # if we are here it means the record is valid, push it to mysql
        record_df = pd.DataFrame([final_record])
        push_dataframe_to_mysql(df=record_df, table_name=Tables.CLOTHS)
        # upload the image to the correct place
        self._upload_image()

        # return True, because updating has been done
        return True

    def run(self) -> bool:
        """
        Returns True if one value or more have been updated, False otherwise.
        """
        familiar_updating_flag = self._update_familiar_products()
        new_product_updating_flag = self._insert_new_product()

        # if there was data to update/insert return True, otherwise False
        return familiar_updating_flag or new_product_updating_flag
