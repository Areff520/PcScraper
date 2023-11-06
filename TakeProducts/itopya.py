import requests
from bs4 import BeautifulSoup as bs4


def get_itopya_products_links():
    """Return product links in dictionary with price attached to it"""
    result = requests.get('https://www.itopya.com/HazirSistemler?sayfa=1&stok=stokvar')
    soup = bs4(result.content)
    page_count = soup.find('span', class_='page-info').find('strong')
    page_count = page_count.text.strip().split('/')

    href_price_dict = {}
    for page_number in range(1,int(page_count[1])+1):
        print('at page', page_number)
        retries = 0
        while retries < 3:
            try:
                result = requests.get(f'https://www.itopya.com/HazirSistemler?sayfa=1&stok=stokvar&pg={page_number}')
                soup = bs4(result.content, features="html.parser")
                product_list = soup.find(id='productList').find_all(class_='product')
                for element in product_list:
                    link_element = element.find(class_='product-header').find('a').get('href')
                    price = element.find(class_='product-footer').find(class_='price').text.strip().replace('.','').split(',')
                    price = price[0]
                    href_price_dict[link_element] = price
                    print(link_element)

                break
            except:
                retries += 1

    print(f'Found {len(href_price_dict.keys())} products in İtopya\n\n')
    return href_price_dict


def check_itopya_details(href_dict):
    """Get product details from the site. If the product specification for the category_list items is empty
    then add a status to skip the product

    if product category out of stock then adds product_dict['status'] = 'skip'

    :returns
    products dict [main product_name]
    products dict has 1 dict and 1 image link inside, link  and 1 price tag
    Inside dict has products[product_category] = [product_title]

    """

    products = {}
    category_list = ['işlemci', 'anakart', 'ekran kartı']
    for link, price in href_dict.items():
        status = True
        product_dict = {}
        link = f'https://www.itopya.com{link}'
        result = requests.get(link)
        soup = bs4(result.content, features="html.parser")
        tables = soup.find('div', id='accordion-itopya').find_all('div', class_='card mb-3')
        image = soup.find(id='anaUrunResmi').get('src')
        main_title = soup.find('h6').text.strip()
        print(main_title)

        for table in tables:
            product_category = table.find('div', class_='title').text.strip().lower()
            title = table.find(class_='product-card active')
            if title:
                title = title.find(class_='product-card-body').find(class_='name secLink').text.strip()
                if product_category == 'bilgisayar kasaları':
                    product_category = 'kasa'
                elif product_category == 'i̇şlemci soğutucular':
                    product_category = 'soğutucu'
                elif product_category == 'ram bellek':
                    product_category = 'ram'
                elif product_category == 'powersupply':
                    product_category = 'güç'


                if product_category != 'montaj ve kurulum':
                    product_dict[product_category] = title
            else:
                """if product category out of stock does not exists then dont add this product to category"""
                if product_category in category_list:
                    status = False
                    break


        if status:
            products[main_title] = [product_dict, image, link, price]
            for key, value in product_dict.items():
                print(f'{key}: {value}')
            print(products)
            print(image, '\n')

    print(products)
    return products

def get_itopya_products():
    links = get_itopya_products_links()
    all_products_dict = check_itopya_details(links)
    return all_products_dict
