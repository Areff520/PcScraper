import traceback
import requests
from bs4 import BeautifulSoup as bs4
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_gamegaraj_products_list():
    """Returns all of the listing in the website"""
    retries = 0
    href_list = []
    while retries < 50:
        try:
            #result = requests.get('https://pckolik.com/kategori/kisisel-bilgisayarlar/hazir-sistemler/?per_page=45')

            for number in range(0,4):
                result = requests.get(f'https://www.gamegaraj.com/grup/firsat-urunler/page/{number}')
                soup = bs4(result.content, features="html.parser")
                product_list = soup.find_all('h2')
                for product_wrapper in product_list:
                    link = product_wrapper.find('a').get('href')
                    href_list.append(link)
            break
        except:
            retries +=1
            traceback.print_exc()
    print(href_list)
    return href_list

def check_gamegaraj_details(href_list):
    """
    :returns
    products dict [main product_name]
    products dict has 1 dict and 1 image href inside, href  and 1 price tag
    Inside dict has products[product_category] = [product_title]

    """
    products = {}
    count = 0
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    for href in href_list:
        retries = 0
        while retries < 3:
            try:
                print('\n')
                print('GameGaraj')
                print(href)
                driver.get(href)
                main_title = driver.find_element(By.CLASS_NAME, 'edgtf-single-product-title').text

                page_loaded = True
                while page_loaded:
                    page_html = driver.find_element(By.TAG_NAME, 'body').get_attribute('outerHTML')
                    if 'Yükleniyor…' in page_html:
                        time.sleep(1)
                    else:
                        page_loaded = False
                print(main_title)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'slick-track' )))
                image = driver.find_element(By.CLASS_NAME, 'slick-track').find_elements(By.TAG_NAME, 'div')[1]\
                    .find_element(By.TAG_NAME, 'img').get_attribute('data-o_img')
                print(image)
                price_string = driver.find_element(By.CLASS_NAME, 'woocommerce-Price-amount').text.strip().replace('TL','').replace(',','')
                price = int(price_string)

                tables = driver.find_elements(By.CLASS_NAME, 'composite_component')
                product_dict = {}
                for row in tables:
                    """passing first two tables"""
                    product_category = row.find_element(By.CLASS_NAME, 'component_title_text').text.strip().lower()
                    product_title = row.find_element(By.XPATH, ".//option[@selected='selected']").text

                    if product_category == 'kasa/güç kaynağı':
                        product_category = 'kasa'
                    elif product_category == 'i̇şlemci':
                        product_category = 'i̇şlemci'
                    elif product_category == 'depolama m.2' or product_category =='depolama':
                        product_category = 'ssd'
                    elif 'ram' in product_category or product_category == 'bellek':
                        product_category = 'ram'
                    elif product_category == 'güç kaynağı' or product_category == 'güç kaynağı 2':
                        product_category = 'güç'
                    elif product_category == 'işlemci soğutucusu':
                        product_category = 'soğutucu'
                    elif product_category == 'ekran kartı':
                        product_title = product_title.replace('RTX','RTX ').replace('RX', 'RX ').replace('XT', ' XT')\
                            .replace('Ti', ' TI')

                    if product_title == 'Seçili Ürün Yok' or product_category == 'i̇şletim sistemi':
                        continue
                    elif product_category == '' or product_title == '':
                        continue
                    if 'Yükleniyor…' not in product_title:
                        product_dict[product_category] = product_title
                        print(product_category,':', product_title)
                products[main_title] = [product_dict, image, href, price]
                count +=1
                break
            except:
                retries += 1
                traceback.print_exc()
    driver.close()

    return products


def get_gamegaraj_products():
    links = get_gamegaraj_products_list()
    all_products_dict = check_gamegaraj_details(links)
    return all_products_dict

