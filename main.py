import time
import traceback

import s3_storage
from TakeProducts import gaminggentr
from TakeProducts import itopya
from TakeProducts import sinerji
from TakeProducts import pckolik
from TakeProducts import gamegaraj
import pandas as pd
from get_price import akakce
from get_price import cimri
from s3_storage import add_image
import db_operations
import the_dict
from get_price import exceptions_akakce
from edit_product_values import make_additional_product_detail
from get_price.difference import calculate_worth
def automation():
    print('Started to work on Automation')

    pckolik_products = pckolik.get_pckolik_products()
    sinerji_products = sinerji.get_sinerji_products()
    gaminggentr_products = gaminggentr.get_gaminggentr_products()
    itopya_products = itopya.get_itopya_products()
    gamegaraj_products = gamegaraj.get_gamegaraj_products()
    print(the_dict.checkpoint)

    all_products_dict = {}
    all_products_dict.update(pckolik_products)
    all_products_dict.update(sinerji_products)
    all_products_dict.update(gaminggentr_products)
    all_products_dict.update(itopya_products)
    all_products_dict.update(gamegaraj_products)

    untouched_all_products_dict = all_products_dict.copy()
    to_be_tested_dict = db_operations.check_if_same_exists_postgres(all_products_dict)

    with open('dict_text.txt', 'w', encoding='utf-8') as file:
        file.write(f'pckolik {len(pckolik_products)},sinerji_products {len(sinerji_products)},gaminggentr_products {len(gaminggentr_products)}\
        , itopya_products {len(itopya_products)}, gamegaraj_products{len(gamegaraj_products)}\
         \n\nuntouched_all_products_dict = {untouched_all_products_dict} \n all_products_dict = {all_products_dict}')

    succesfull_dict, unsuccesfull_dict = akakce.get_price_akakce(to_be_tested_dict)

    to_be_updated_pc_list = calculate_worth(succesfull_dict)
    with open('dict_text.txt', 'a', encoding='utf-8') as file:
        file.write(f'\n\nsucessfull_dict = {succesfull_dict}\n\nto_be_updated_pc_list = {to_be_updated_pc_list}')
    print(the_dict.checkpoint)

    copy_updated_list = to_be_updated_pc_list.copy()
    #Updating images of succesfull products
    for pc_dict in copy_updated_list:
        for key, values in pc_dict.items():
            name = key
            image = values[1]
            print()
            print(name)
            print(image)
            if image is not None:
                try:
                    s3_storage.add_image(image, name)
                except:
                    to_be_updated_pc_list.remove(pc_dict)
                    print('EXCEPTION')
            else:
                to_be_updated_pc_list.remove(pc_dict)
                untouched_all_products_dict.pop(key)
                print('REMOVED')
        db_operations.populate_main_page_product_db(pc_dict)
    #Updating image of all products
    for key, values in untouched_all_products_dict.items():
        name = key
        image = values[1]
        if image is not None:
            try:
                s3_storage.add_image(image, name)
            except:
                print('EXCEPTION')
        else:
            untouched_all_products_dict.pop(key)
            print('REMOVED')

    additional_product_detail_tuples_list = make_additional_product_detail(untouched_all_products_dict)
    db_operations.populate_main_product_details_db(additional_product_detail_tuples_list)
    db_operations.delete_rows(untouched_all_products_dict)
    s3_storage.remove_image()


automation()
