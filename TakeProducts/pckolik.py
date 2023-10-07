import traceback

import requests
from bs4 import BeautifulSoup as bs4

def get_pckolik_products_list():
    """Returns all of the listing in the website"""
    retries = 0
    href_list = []
    while retries < 50:
        try:
            #result = requests.get('https://pckolik.com/kategori/kisisel-bilgisayarlar/hazir-sistemler/?per_page=45')

            for number in range(0,10):
                result = requests.get(f'https://pckolik.com/kategori/kisisel-bilgisayarlar/hazir-sistemler/page/{number}')
                soup = bs4(result.content, features="html.parser")
                product_list = soup.find_all(class_='product-wrapper')
                for product_wrapper in product_list:
                    link = product_wrapper.find('a').get('href')
                    href_list.append(link)
            break
        except:
            retries +=1
            traceback.print_exc()
    return href_list

def check_pckolik_details(href_list):
    """
    :returns
    products dict [main product_name]
    products dict has 1 dict and 1 image href inside, href  and 1 price tag
    Inside dict has products[product_category] = [product_title]

    """
    products = {}
    count = 0
    for href in href_list:
        retries = 0
        while retries < 3:
            try:
                print('\n')
                print('PC KOLIK')
                print(href)
                result = requests.get(href)
                soup = bs4(result.content, features="html.parser")

                check_if_stock = soup.find('button', string='Stoklar tükendi')
                if not check_if_stock:
                    main_title = soup.find('h1').get_text().strip()
                    print(main_title)
                    image = soup.find(class_='wp-post-image').get('data-src')
                    price_string = soup.find('p', class_='price').find('ins').find('bdi').get_text().strip().replace(',','').split('.')
                    price = ''
                    for price_tag in price_string[0:1]:
                        price += price_tag


                    tables = soup.find( class_='woocommerce-product-attributes shop_attributes').find_all('tr')
                    product_dict = {}
                    for row in tables:
                        """passing first two tables"""
                        product_category = row.find('th').find('span').get_text().strip().lower()
                        product_title = row.find('td').find('p').get_text().strip()
                        if product_category == 'bilgisayar kasası':
                            product_category = 'kasa'
                        elif product_category == 'i̇şlemci modeli':
                            product_category = 'i̇şlemci'
                        elif product_category == 'depolama':
                            product_category = 'ssd'
                        elif product_category == 'bellek':
                            product_category = 'ram'
                        elif product_category == 'güç kaynağı':
                            product_category = 'güç'
                        elif product_category == 'işlemci soğutucusu':
                            product_category = 'soğutucu'

                        product_dict[product_category] = product_title
                        print(product_category,': ', product_title)
                    products[main_title] = [product_dict, image, href, price]
                    count +=1
                break
            except:
                retries += 1

    return products


def get_pckolik_products():
    links = get_pckolik_products_list()
    all_products_dict = check_pckolik_details(links)
    return all_products_dict

