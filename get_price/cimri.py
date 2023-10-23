import traceback

import bs4 as bs4
import requests
from bs4 import BeautifulSoup as bs4
from random import randint

def give_header():
    """Gives additional headers to scrape from akakce"""
    SCRAPEOPS_API_KEY = 'b32f312c-cc84-450c-8810-ce60ee5d14cb'

    def get_headers_list():
        response = requests.get('http://headers.scrapeops.io/v1/browser-headers?api_key=' + SCRAPEOPS_API_KEY)
        json_response = response.json()
        return json_response.get('result', [])

    def get_random_header(header_list):
        random_index = randint(0, len(header_list) - 1)
        return header_list[random_index]
    header_list = get_headers_list()
    return get_random_header(header_list)

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
                header = {'upgrade-insecure-requests': '1',
                          'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
                          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                          'sec-ch-ua': 'Google Chrome;v="89", "Chromium";v="89", ";Not A Brand";v="99"',
                          'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': 'macOS', 'sec-fetch-site': 'none',
                          'sec-fetch-mod': '', 'sec-fetch-user': '?1', 'accept-encoding': 'gzip, deflate',
                          'accept-language': 'en-US'}
                link = f'https://www.cimri.com/arama?q={product_name}'
                if product_category == 'ekran kartı':
                    link = f'https://www.cimri.com/ekran-kartlari?q={product_name}'
                params = None
                while retries < 30:
                    try:
                        result = requests.get(link, headers=header, params=params)
                        soup = bs4(result.content, features="html.parser")
                        price = soup.find(id='cimri-product').find(class_='top-offers').find('a').get_text()
                        index_of_first_numeric = next((i for i, char in enumerate(price) if char.isdigit()),
                                                      None)
                        price = price[index_of_first_numeric:].replace('.','').split(',')
                        total_price += int(price[0])
                        break
                    except:
                        if retries == 28:
                            print('SCRAPERIO BEEN USED')
                            params = {
                                'api_key': 'b32f312c-cc84-450c-8810-ce60ee5d14cb',
                                'url': f'{link}',
                            }
                            link = 'https://proxy.scrapeops.io/v1/'
                            header = give_header()
                        retries += 1
                if retries == 30:
                    print('FAILED')
                print(product_name, int(price[0]))
            new_values = values + [total_price]
            succesfull_dict[product_main_name] = new_values
            print(f'Cimri; Original price vs total price is {original_price} vs {total_price} and the difference is {original_price-total_price}')

        except:
            print(soup)


    print(succesfull_dict)
    return succesfull_dict
