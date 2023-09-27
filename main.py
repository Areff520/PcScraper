
from TakeProducts import gaminggentr
from TakeProducts import itopya
import pandas as pd
from GetPrice import akakce
from GetPrice import cimri
from the_dict import final_dict_all
from add_image_s3 import add_image
import update_db


def calculate_worth(succesfulL_dict):
    columns = ['Title','Org Price','Solo Price','Difference','link']
    df = pd.DataFrame(columns=columns)
    passed_dicts = []
    for key, values in succesfulL_dict.items():
        print()
        link = values[2]
        original_price = int(values[3])
        solo_price = int(values[4])
        difference = original_price-solo_price

        if difference < 0:
            difference = 100 * abs(difference) / solo_price
            difference = str(difference).split('.')
            difference = int(difference[0])
            if difference > 10:
                new_row = {'Title': key, 'Org Price':original_price, 'Solo Price':solo_price,'Difference':difference ,'link':link}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                values.append(difference)
                passed_dicts.append({key:values})
    result = 'result.xlsx'
    df.to_excel(result, index=False)
    return passed_dicts
def fnc():
    gaminggentr_links = gaminggentr.get_gaminggentr_products()
    gaminggentr_products = gaminggentr.check_gaminggentr_details(gaminggentr_links)
    itopya_links = itopya.get_itopya_products()
    itoya_products = itopya.check_itopya_details(itopya_links)
    all_products_dict = {}
    all_products_dict.update(itoya_products)
    all_products_dict.update(gaminggentr_products)

    succesfull_dict, unsuccesfull_dict = akakce.get_price_akakce(all_products_dict)
    print(succesfull_dict)
    cimri_dict = cimri.get_price_cimri(unsuccesfull_dict)
    print(succesfull_dict)
    print(unsuccesfull_dict)
    succesfull_dict.update(cimri_dict)
    print(succesfull_dict)

    to_be_updated_pc_list = calculate_worth(succesfull_dict)

    for pc_dict in to_be_updated_pc_list:
        for key, values in pc_dict.items():
            name = key
            image = values[1]
            # add_image(image, name)

        update_db.update_postgres_db(pc_dict)

    pass



to_be_updated_pc_list = calculate_worth(final_dict_all)

