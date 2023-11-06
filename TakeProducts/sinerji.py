import traceback

import requests
from bs4 import BeautifulSoup as bs4

def get_sinerji_products_list():
    """Returns all of the listing in the website on list format"""
    header = {'upgrade-insecure-requests': '1',
              'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
              'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
              'sec-ch-ua': 'Google Chrome;v="89", "Chromium";v="89", ";Not A Brand";v="99"',
              'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': 'macOS', 'sec-fetch-site': 'none',
              'sec-fetch-mod': '', 'sec-fetch-user': '?1', 'accept-encoding': 'gzip, deflate',
              'accept-language': 'en-US'}

    retries = 0
    product_href_list = []

    while retries < 10:
        try:
            result = requests.get('https://www.sinerji.gen.tr/oyun-bilgisayari-c-2116?sx=BestSellers', headers=header)
            soup = bs4(result.content, features="html.parser")
            page_count = soup.find(class_='paging').find_all('a')
            page_count = page_count[-2].text.strip()
            for page in range(1, int(page_count)+ 1):
                result = requests.get(f'https://www.sinerji.gen.tr/oyun-bilgisayari-c-2116?sx=BestSellers&px={page}',
                                      headers=header)
                soup = bs4(result.content, features="html.parser")
                product_list = soup.find_all(class_='col-xl-3')
                for product_wrapper in product_list:
                    link = product_wrapper.find('a').get('href')
                    product_href_list.append(link)
            break
        except:
            retries +=1
            traceback.print_exc()
    return product_href_list

def check_sinerji_details(href_list):
    """
    :returns
    products dict [main product_name]
    products dict has 1 dict and 1 image href inside, href  and 1 price tag
    Inside dict has products[product_category] = [product_title]

    """
    products = {}
    for href in href_list:
        try:
            print('\n')
            href = f'https://www.sinerji.gen.tr{href}'
            result = requests.get(href)
            soup = bs4(result.content, features="html.parser")

            main_title = soup.find('h1').get_text().strip()
            image = soup.find('a', class_='productPhotoCarouselPhotoLink').get('data-img')
            price = soup.find('span', class_='price').find('span').get_text().strip().replace('.','').split(",")
            price = price[0]

            tables = soup.find_all( class_='row preBuiltPcCategory')
            product_dict = {}
            for table in tables[2:]:
                """passing first two tables"""
                product_category = table.find('h3').get_text().strip().lower()
                rows = table.find_all(class_='preBuiltPcProduct')
                for row in rows:
                    if row.get('data-isdefault') == 'true':
                        title_element = row.find('label')
                        product_title = title_element.get_text().strip().replace('ÖNERİLEN', '').replace('İNDİRİM', '').replace('\n', '')
                        if product_title.endswith("i"):
                            product_title = product_title[::-1].replace("i", "", 1)[
                                            ::-1]
                        if product_category == 'bilgisayar kasası':
                            product_category = 'kasa'
                        elif product_category == 'i̇şlemci soğutucu':
                            product_category = 'soğutucu'
                        elif product_category == 'ssd disk':
                            product_category = 'ssd'
                        elif product_category == 'bellek (ram)':
                            product_category = 'ram'
                        elif product_category == 'güç kaynağı':
                            product_category = 'güç'
                        elif product_category == 'i̇şlemci':
                            product_category = 'işlemci'

                        product_dict[product_category] = product_title

            products[main_title] = [product_dict, image, href, price]
            print(main_title)
            for key, value in product_dict.items():
                print(f'{key}: {value}')
        except:
            print('Error occured passing href', href)

    return products

def get_sinerji_products():
    links = get_sinerji_products_list()
    all_products_dict = check_sinerji_details(links)
    return all_products_dict

