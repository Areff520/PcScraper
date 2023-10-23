import re
import traceback

import requests
from bs4 import BeautifulSoup as bs4
from random import randint
from .exceptions_akakce import exception_akakce
import pandas as pd

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


def get_price_akakce(product_dict):
    """Takes the product dict and finds every price of individual item.
        detail dict: işlemci, anakart, ram, ekran kartı, kasa ,güç ,soğutucu, ssd

        :return
        succesfull_dict['main_title']=[detail_dict, image, link, site_price, akakce_price]
        unsuccesfull_dict = product_dict_price['main_title]=[detail_dict, image, link, site_price]
    """
    succesfull_dict = {}
    unsuccesfull_dict = {}
    df = temp_excel()

    for counter, (product_main_name, values) in enumerate(product_dict.items()):
        status = True
        print('\n\nWorking on new ticket', product_main_name)
        print(f'Counter is {counter} / {len(product_dict.keys())}')
        print(values[2])
        print(values)
        product_details_dict = values[0]
        original_price = int(values[3])


        total_price = 0

        category_name_string = ''
        link_string = ''
        for product_category, product_name in product_details_dict.items():
            product_name = product_name.lower()
            if product_category == 'i̇şlemci':
                product_name = product_name.replace(' core', '')
                if 'ghz' in product_name or 'ghz' in product_name:
                    product_name_splitted = product_name.split()
                    product_name = ''
                    for index, word in enumerate(product_name_splitted):
                        if 'ghz' in word:
                            split_count = index
                    for word in product_name_splitted[0:split_count]:
                        product_name += f'{word} '
                if 'i3-12100f' in product_name:
                    product_name = 'intel i3-12100f'
                link = f'https://www.akakce.com/arama/?q={product_name}&c=1030'

            elif product_category == 'anakart':
                if 'mhz' in product_name:
                    product_name_splitted = product_name.split()
                    product_name = ''
                    for index, word in enumerate(product_name_splitted):
                        if 'mhz' in word:
                            split_count = index
                    for word in product_name_splitted[0:split_count]:
                        product_name += f'{word} '
                link = f'https://www.akakce.com/arama/?q={product_name}&c=1032'

            elif product_category == 'ram':
                link = f'https://www.akakce.com/arama/?q={product_name}&c=1036'

            elif product_category == 'ekran kartı':
                product_name = product_name.replace('geforce', '').replace('radeon', '')
                pattern = re.compile(r'\d+\s*GB', re.IGNORECASE)
                if ' oc' in product_name:
                    """Taking string before oc"""
                    product_name = (product_name.split('oc'))[0]
                if pattern.search(product_name):
                    product_name_splitted = product_name.split()
                    product_name = ''
                    for index, word in enumerate(product_name_splitted):
                        if pattern.search(word):
                            split_count = index
                    for word in product_name_splitted[0:split_count]:
                        product_name += f'{word} '

                link = f'https://www.akakce.com/arama/?q={product_name}&c=1053'

            elif product_category == 'kasa':
                link = f'https://www.akakce.com/arama/?q={product_name}&c=1050'
            elif product_category == 'ssd':
                link = f'https://www.akakce.com/arama/?q={product_name}&c=17961'
            elif product_category == 'soğutucu':
                link = f'https://www.akakce.com/arama/?q={product_name}&c=18559'
            elif product_category == 'güç':
                link = f'https://www.akakce.com/arama/?q={product_name}&c=1103'
            else:
                link = f'https://www.akakce.com/arama/?q={product_name}'

            product_name, link = exception_akakce(product_name, link=link, product_category=product_category)

            retries = 0
            try_no_filter = 0
            header = {'upgrade-insecure-requests': '1',
                      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
                      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                      'sec-ch-ua': 'Google Chrome;v="89", "Chromium";v="89", ";Not A Brand";v="99"',
                      'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': 'macOS', 'sec-fetch-site': 'none',
                      'sec-fetch-mod': '', 'sec-fetch-user': '?1', 'accept-encoding': 'gzip, deflate',
                      'accept-language': 'en-US'}
            params = None
            link_changed = 'No'
            count_for_exception_akakce = 0
            while retries < 30:
                try:
                    result = requests.get(link, headers=header, params=params)
                    soup = bs4(result.content, features="html.parser")

                    """Choosing the product model for GPU's"""
                    if product_category == 'ekran kartı':
                        labels = soup.find(id='FF_v8').find_all('label')
                        for label in labels:
                            label_text = label.get_text().strip().lower()
                            pattern = re.compile(r'\s.*\d|\d.*\s')
                            if label_text in product_name and pattern.search(label_text) and link_changed =='No':
                                input_element = label.find('input')
                                value = input_element.get('value')
                                name = input_element.get('name')
                                link = f'{link}&{name}={value}'
                                link_changed = 'Yes'
                                print('Link Changed for GPU')

                                assert False
                    price = soup.find(id='APL').find(class_='pt_v9').text.strip().split(',')
                    price = price[0].replace('.', '')
                    if product_category == 'ssd' and int(price) > 4000:
                        price = exception_akakce(product_name, price=int(price), product_category=product_category)
                    elif product_category == 'ram' and '8gb' in product_name and '16gb' not in product_name\
                            or int(price) < 1000 and product_category == 'ram' :
                        price = int(price) * 2
                    elif product_category == 'güç' and int(price) > 8500 and 'için herhangi bir ürün bulunamadı.' in soup.get_text():
                        if '700' in product_name:
                            price = 4000
                        elif '800' in product_name:
                            price = 5000
                        else:
                            price = 2000

                    #işlemci soğutucularda hata çıkartıyor
                    if 'için herhangi bir ürün bulunamadı.' in soup.get_text() and count_for_exception_akakce == 0:
                        product_name, link = exception_akakce(product_name=product_name, link=link, product_not_found=True)
                        count_for_exception_akakce += 1
                        assert False
                    elif 'için herhangi bir ürün bulunamadı.' in soup.get_text() and count_for_exception_akakce > 0 and int(price) > 10000:
                        print('THAT IS FALSE')
                        status = False
                    total_price += int(price)
                    print(product_name, f' Retried {retries} times, Price: {price}')
                    category_name_string = category_name_string + f'{product_category}: {price}    '
                    link_string = link_string + f'{link} '
                    break
                except:

                    if retries == 27:
                        print('SCRAPERIO BEEN USED')
                        params = {
                            'api_key': 'b32f312c-cc84-450c-8810-ce60ee5d14cb',
                            'url': f'{link}',
                        }
                        link = 'https://proxy.scrapeops.io/v1/'
                        header = give_header()
                    if 'için hiç ürün bulunamadı' in soup.get_text():
                        link = f'https://www.akakce.com/arama/?q={product_name}'
                        print('ÜRÜN BULUNAMADI')
                        if try_no_filter > 0:
                            unsuccesfull_dict[product_main_name] = values
                            status = False
                            try_no_filter += 1
                            print('STATUS FALSE')
                            break
                    if 'için herhangi bir ürün bulunamadı.' in soup.get_text() and try_no_filter == 0:
                        link = f'https://www.akakce.com/arama/?q={product_name}'
                    retries += 1
            if retries == 30:
                print('FAILED')
                status = False
                break
        if status:
            new_values = values + [total_price]
            succesfull_dict[product_main_name] = new_values
            new_row = {"name": product_main_name, "price": category_name_string, "link": link_string,"total price": total_price, "diff":original_price-total_price, "original price":original_price}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            result = 'price_tags.xlsx'
            df.to_excel(result, index=False)
            print(f'Akakçe; Original price vs total price is {original_price} vs {total_price} and the difference is {original_price-total_price}')



    print(succesfull_dict)
    return succesfull_dict, unsuccesfull_dict



def akakce_search(product_name,link,header):
    result = requests.get(link, headers=header, proxies=None)
    soup = bs4(result.content, features="html.parser")
    price = soup.find(id='APL').find(class_='pt_v9').text.strip().split(',')
    price = price[0].replace('.', '')
    print(product_name, price)
    return int(price)

def temp_excel():
    data = {"name":[],"total price":[], "original price":[],"diff":[], "price":[] ,"link":[]}
    df = pd.DataFrame(data)
    return df