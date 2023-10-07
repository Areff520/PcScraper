import time

import s3_storage
from TakeProducts import gaminggentr
from TakeProducts import itopya
from TakeProducts import sinerji
from TakeProducts import pckolik
import pandas as pd
from GetPrice import akakce
from GetPrice import cimri
from s3_storage import add_image
import db_operations
import the_dict
from GetPrice import exceptions_akakce

def calculate_worth(succesfulL_dict):
    """Takes dict

    :return
    list
    """
    columns = ['Title','Org Price','Solo Price','Difference','link']
    df = pd.DataFrame(columns=columns)
    passed_dicts = []
    for key, values in succesfulL_dict.items():
        link = values[2]
        original_price = int(values[3])
        solo_price = int(values[4])
        difference = original_price-solo_price

        #Getting difference to return as lsit
        if difference < 0:
            difference = 100 * abs(difference) / solo_price
            difference = str(difference).split('.')
            difference = int(difference[0])
            if difference > 10 or difference > 5 and 'aming' not in link:
                values.append(difference)
                passed_dicts.append({key: values})
                new_row = {'Title': key, 'Org Price': original_price, 'Solo Price': solo_price,
                           'Difference': f'-{difference}',
                           'link': link}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        #For excel
        if difference > 0:
            difference = 100 * difference / solo_price
            difference = str(difference).split('.')
            difference = int(difference[0])
            new_row = {'Title': key, 'Org Price': original_price, 'Solo Price': solo_price, 'Difference': difference,
                       'link': link}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    result = 'result.xlsx'
    df.to_excel(result, index=False)

    return passed_dicts
def automation():
    print('Started to work on Automation')
    pckolik_products = pckolik.get_pckolik_products()
    sinerji_products = sinerji.get_sinerji_products()
    gaminggentr_products = gaminggentr.get_gaminggentr_products()
    itopya_products = itopya.get_itopya_products()
    print(the_dict.checkpoint)

    all_products_dict = {}
    all_products_dict.update(pckolik_products)
    all_products_dict.update(sinerji_products)
    all_products_dict.update(gaminggentr_products)
    all_products_dict.update(itopya_products)
    print(f'pckolik {len(pckolik_products)},sinerji_products {len(sinerji_products)},gaminggentr_products {len(gaminggentr_products)}, itopya_products {len(itopya_products)}')
    print('All product dict len is ', len(all_products_dict))
    all_products_dict, price_didnot_change_dict = db_operations.update_local_db(all_products_dict)

    with open('dict_text.txt', 'w', encoding='utf-8') as file:
        file.write(f'\n\nall_products_dict = {all_products_dict}')

    succesfull_dict, unsuccesfull_dict = akakce.get_price_akakce(all_products_dict)
    with open('dict_text.txt', 'a', encoding='utf-8') as file:
        file.write(f'\n\nsuccesfull_dict = {succesfull_dict}')
        file.write(f'\n\nunsuccesfull_dict = {unsuccesfull_dict}')
    print(the_dict.checkpoint)

    cimri_dict = cimri.get_price_cimri(unsuccesfull_dict)
    succesfull_dict.update(cimri_dict)
    with open('dict_text.txt', 'a', encoding='utf-8') as file:
        file.write(f'\n\nsuccesfull_updated_dict = {succesfull_dict}')
    print(the_dict.checkpoint)

    to_be_updated_pc_list = calculate_worth(succesfull_dict)
    with open('dict_text.txt', 'a', encoding='utf-8') as file:
        file.write(f'\n\nto_be_updated_pc_list = {to_be_updated_pc_list}')
    print(the_dict.checkpoint)

    for pc_dict in to_be_updated_pc_list:
        for key, values in pc_dict.items():
            name = key
            image = values[1]
            s3_storage.add_image(image, name)
        db_operations.update_postgres_db(pc_dict)

    db_operations.delete_rows(to_be_updated_pc_list, price_didnot_change_dict)

automation()