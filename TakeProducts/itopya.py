import time
import traceback

import requests
from bs4 import BeautifulSoup as bs4
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service


def wait_for_page_load(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )

def get_itopya_products_links():
    """Return product links in dictionary with price attached to it"""
    result = requests.get('https://www.itopya.com/HazirSistemler?sayfa=1&stok=stokvar', verify=False)
    soup = bs4(result.content)
    page_count = soup.find('span', class_='page-info').find('strong')
    page_count = page_count.text.strip().split('/')

    href_price_dict = {}
    for page_number in range(1,int(page_count[1])+1):
        print('at page', page_number)
        retries = 0
        while retries < 3:
            try:
                result = requests.get(f'https://www.itopya.com/HazirSistemler?sayfa=1&stok=stokvar&pg={page_number}', verify=False)
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
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    products = {}
    category_list = ['işlemci', 'anakart', 'ekran kartı']
    for link, price in href_dict.items():
        try:
            status = True
            product_dict = {}
            link = f'https://www.itopya.com{link}'
            print(link)
            driver.get(link)
            result = driver.page_source
            wait_for_page_load(driver)
            soup = bs4(result, features="html.parser")
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
            price = driver.find_element(By.CLASS_NAME, 'price.mt-3.mt-md-0').find_element(By.TAG_NAME, 'fiyatspan').text.strip().replace('.','').split(',')
            if price == ['']:
                result = driver.page_source
                soup = bs4(result, features="html.parser")
                soup_price = soup.find('fiyatspan')
                price = soup_price.get_text().strip().replace('.','').split(',')
            price = int(price[0])
            if status:
                products[main_title] = [product_dict, image, link, price]
                for key, value in product_dict.items():
                    print(f'{key}: {value}')
                print(image, '\n')
        except:
            traceback.print_exc()
    return products

def get_itopya_products():
    links = get_itopya_products_links()
    #links = {'/spunkram-photoshopintel-core-i7-13700kasus-geforce-rtx-4070-ti-proart-oc-12gb16gb-ddr41tb-nvme-m_h24290':5}
    all_products_dict = check_itopya_details(links)
    return all_products_dict


