import aiohttp
from bs4 import BeautifulSoup as bs4
import asyncio
import traceback

async def fetch(session, url):
    headers = {'upgrade-insecure-requests': '1',
              'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
              'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
              'sec-ch-ua': 'Google Chrome;v="89", "Chromium";v="89", ";Not A Brand";v="99"',
              'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': 'macOS', 'sec-fetch-site': 'none',
              'sec-fetch-mod': '', 'sec-fetch-user': '?1', 'accept-encoding': 'gzip, deflate',
              'accept-language': 'en-US'}
    async with session.get(url, headers=headers) as response:
        return await response.text()

async def get_pckolik_products_list():
    """Returns all of the listing in the website"""
    retries = 0
    href_list = []
    while retries < 50:
        try:
            async with aiohttp.ClientSession() as session:
                for number in range(0, 10):
                    result = await fetch(session, f'https://pckolik.com/kategori/kisisel-bilgisayarlar/hazir-sistemler/page/{number}')
                    soup = bs4(result, features="html.parser")
                    product_list = soup.find_all(class_='product-wrapper')
                    for product_wrapper in product_list:
                        link = product_wrapper.find('a').get('href')
                        href_list.append(link)
            break
        except Exception as e:
            retries += 1
    return href_list

async def check_pckolik_details(href_list):
    """
    :returns
    products dict [main product_name]
    products dict has 1 dict and 1 image href inside, href  and 1 price tag
    Inside dict has products[product_category] = [product_title]
    """
    products = {}
    async with aiohttp.ClientSession() as session:
        for href in href_list:
            retries = 0
            while retries < 3:
                try:
                    print('\n')
                    print('PC KOLIK')
                    print(href)
                    result = await fetch(session, href)
                    soup = bs4(result, features="html.parser")

                    check_if_stock = soup.find('button', string='Stoklar tükendi')
                    if not check_if_stock:
                        main_title = soup.find('h1').get_text().strip()
                        print(main_title)
                        image = soup.find(class_='wp-post-image').get('data-src')
                        price_string = soup.find('p', class_='price').find('ins').find('bdi').get_text().strip().replace(',','').split('.')
                        price = ''.join(price_string[0:1])

                        tables = soup.find(class_='woocommerce-product-attributes shop_attributes').find_all('tr')
                        product_dict = {}
                        for row in tables:
                            product_category = row.find('th').find('span').get_text().strip().lower()
                            product_title = row.find('td').find('p').get_text().strip()
                            # Mapping of product categories
                            product_category = product_category.replace('bilgisayar kasası', 'kasa') \
                                .replace('i̇şlemci modeli', 'i̇şlemci') \
                                .replace('depolama', 'ssd') \
                                .replace('bellek', 'ram') \
                                .replace('güç kaynağı', 'güç') \
                                .replace('işlemci soğutucusu', 'soğutucu')

                            product_dict[product_category] = product_title
                            print(product_category, ': ', product_title)
                        products[main_title] = [product_dict, image, href, price]
                    break
                except Exception as e:
                    retries += 1
                    print(traceback.format_exc())
    print(products)
    return products

async def get_pckolik_products():
    links = await get_pckolik_products_list()
    all_products_dict = await check_pckolik_details(links)
    return all_products_dict


