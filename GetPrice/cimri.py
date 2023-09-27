import traceback

import bs4 as bs4
import requests
from bs4 import BeautifulSoup as bs4

def get_price_cimri(product_dict):
    """Takes the product dict and finds every price of individual item.

        :return
        product_dict_price['main_title]=[detail_dict, image, site_price, akakce_price]
    """
    succesfull_dict = {}
    for product_main_name, values in product_dict.items():
        try:
            status = True
            print('\n\nWorking on new ticket', product_main_name)
            product_details_dict = values[0]
            original_price = int(values[3])

            total_price = 0
            for product_category, product_name in product_details_dict.items():
                retries = 0
                while retries < 100:
                    try:
                        result = requests.get(f'https://www.cimri.com/arama?q={product_name}')
                        soup = bs4(result.content, features="html.parser")
                        price = soup.find(id='cimri-product').find(class_='top-offers').find('a').get_text()
                        index_of_first_numeric = next((i for i, char in enumerate(price) if char.isdigit()),
                                                      None)
                        price = price[index_of_first_numeric:].replace('.','').split(',')
                        total_price += int(price[0])
                        break
                    except:
                        retries += 1
                if retries == 100:
                    print('FAILED')
                print(product_name, int(price[0]))
            new_values = values + [total_price]
            succesfull_dict[product_main_name] = new_values
            print(f'Original price vs total price is {original_price} vs {total_price} and the difference is {original_price-total_price}')

        except:
            print(soup)


    print(succesfull_dict)
    return succesfull_dict
