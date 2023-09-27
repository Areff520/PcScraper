import requests
from bs4 import BeautifulSoup as bs4


def get_gaminggentr_products():
    """Returns all of the listing in the website"""
    result = requests.get('https://www.gaming.gen.tr/kategori/hazir-sistemler/')
    soup = bs4(result.content, features="html.parser")
    page_count_elements = soup.find_all('a', class_='page-numbers')
    page_count = page_count_elements[-2].text

    href_list = []
    for page_number in range(1,int(page_count)+1):
        print('at page', page_number)
        retries = 0
        while retries < 3:
            try:
                result = requests.get(f'https://www.gaming.gen.tr/kategori/hazir-sistemler/page/{page_number}/')
                soup = bs4(result.content, features="html.parser")
                product_list = soup.find('ul', class_='products columns-3').find_all('a')
                for element in product_list:
                    href_list.append(element.get('href'))
                break
            except:
                retries += 1
    print(f'Found {len(href_list)} products in Gaming Gen Tr')
    return href_list


def check_gaminggentr_details(href_list):
    """Create dictionary of all of the available pc's details
        :returns
    products dict [main product_name]
    products dict has 1 dict, image, main_link and price tag
    Inside dict has [product_category] = [product_title]
"""

    products = {}
    for href in href_list:
        retries = 0
        while retries < 3:
            try:
                product_dict = {}

                result = requests.get(href)
                soup = bs4(result.content)
                main_title = soup.find('h1', class_='product_title entry-title').text.strip()
                print(main_title)
                image = soup.find(class_='woocommerce-product-gallery__image').find('img').get('data-src')
                print(image)
                price = soup.find('ins').find(class_='woocommerce-Price-amount amount').text.strip().replace('.','').split(",")
                price = price[0]
                print(price)

                table_rows = soup.find(class_='su-table su-table-responsive su-table-alternate').find_all('tr')
                for row in table_rows[2:]:
                    row = row.find_all('td')
                    product_category = row[0].text.strip().lower()
                    if product_category == 'bilgisayar kasaları':
                        product_category = 'kasa'
                    elif product_category == 'sıvı soğutucu':
                        product_category = 'soğutucu'
                    elif product_category == 'ram bellek':
                        product_category = 'ram'
                    elif product_category == 'güç kaynağı':
                        product_category = 'güç'

                    product_dict[product_category] = row[1].text.strip()
                for key, value in product_dict.items():
                    print(f'{key}: {value}')
                print(' ')
                products[main_title] = [product_dict, image, href, price]
                break
            except:
                retries += 1

    return products
