import time
import traceback

import s3_storage
from TakeProducts import gaminggentr
from TakeProducts import itopya
from TakeProducts import sinerji
from TakeProducts import pckolik
from TakeProducts import gamegaraj
from get_price import akakce
import db_operations
from edit_product_values import make_additional_product_detail
from get_price.difference import calculate_worth
import asyncio
import datetime

async def get_products():
    # Schedule all get product functions to run concurrently.
    tasks = [
        pckolik.get_pckolik_products(),
        sinerji.get_sinerji_products(),
        gaminggentr.get_gaminggentr_products(),
    ]
    results = await asyncio.gather(*tasks)

    pckolik_products, sinerji_products, gaminggentr_products = results
    return pckolik_products, sinerji_products, gaminggentr_products

def automation():
    start_time = datetime.datetime.now()
    print('Started to work on Automation')

    pckolik_products, sinerji_products, gaminggentr_products = asyncio.run(get_products())
    gamegaraj_products = gamegaraj.get_gamegaraj_products()
    itopya_products = itopya.get_itopya_products()
    all_products_dict = {}
    all_products_dict.update(pckolik_products)
    all_products_dict.update(sinerji_products)
    all_products_dict.update(gaminggentr_products)
    all_products_dict.update(itopya_products)
    all_products_dict.update(gamegaraj_products)

    untouched_all_products_dict = all_products_dict.copy()
    to_be_tested_dict = db_operations.check_if_same_exists_postgres(all_products_dict)

    with open('the_dict.py', 'w', encoding='utf-8') as file:
        file.write(f'pckolik = {len(pckolik_products)}\n')
        file.write(f'sinerji_products = {len(sinerji_products)}\n')
        file.write(f'gaminggentr_products = {len(gaminggentr_products)}\n')
        file.write(f'itopya_products = {len(itopya_products)}\n')
        file.write(f'gamegaraj_products = {len(gamegaraj_products)}\n\n')
        file.write(f'untouched_all_products_dict = {untouched_all_products_dict}\n')
        file.write(f'to_be_tested_dict = {to_be_tested_dict}\n')

    succesfull_dict, unsuccesfull_dict = akakce.get_price_akakce(to_be_tested_dict)

    succesfull_to_be_updated = calculate_worth(succesfull_dict)
    with open('the_dict.py', 'a', encoding='utf-8') as file:
        file.write(f'\nsuccesfull_dict = {succesfull_dict}\n')
        file.write(f'\nunsuccesfull_dict = {unsuccesfull_dict}\n')
        file.write(f'succesfull_to_be_updated = {succesfull_to_be_updated}\n')

    #Updating image of all products
    copy_untouched_all_products_dict = untouched_all_products_dict.copy()
    image_list = s3_storage.list_image_names()
    for key, values in copy_untouched_all_products_dict.items():
        name = key
        name_forimage = name.replace('/', ',')
        image = values[1]
        if image is not None and f'pc_images/{name_forimage}.png' not in image_list:
            s3_storage.add_image(image, name)
        else:
            #untouched_all_products_dict.pop(key)
            print('Image allready updated, passing')

    additional_product_detail_tuples_list = make_additional_product_detail(untouched_all_products_dict)
    with open('the_dict.py', 'a', encoding='utf-8') as file:
        file.write(f'\nadditional_product_detail_tuples_list = {additional_product_detail_tuples_list}\n')

    for key, values in succesfull_to_be_updated.items():
        db_operations.populate_main_page_product_db(key, values)
    #Removing succesfull dics so it wont get updated again on Database main_page_product
    succesfull_to_be_updated = succesfull_to_be_updated.keys()
    for key in succesfull_to_be_updated:
        unsuccesfull_dict.pop(key, None)
    #updating Unsuccesfull items
    for key, values in unsuccesfull_dict.items():
        db_operations.populate_main_page_product_db(key, values)

    db_operations.populate_main_product_details_db(additional_product_detail_tuples_list)
    db_operations.change_is_stock_available(untouched_all_products_dict)
    #s3_storage.remove_image()
    print(f'Started at {start_time} and finished at {datetime.datetime.now()}.')
    print(f'Found {len(succesfull_dict.keys()) + len(unsuccesfull_dict.keys())}')
automation()
