import aiohttp
from bs4 import BeautifulSoup as bs4
import asyncio

async def fetch(session, url):
    headers = {'upgrade-insecure-requests': '1',
              'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
              'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
              'sec-ch-ua': 'Google Chrome;v="89", "Chromium";v="89", ";Not A Brand";v="99"',
              'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': 'macOS', 'sec-fetch-site': 'none',
              'sec-fetch-mod': '', 'sec-fetch-user': '?1', 'accept-encoding': 'gzip, deflate',
              'accept-language': 'en-US'}
    async with session.get(url,headers = headers) as response:
        return await response.text()

async def get_gaminggentr_products_links():
    """Returns all of the listing in the website"""
    async with aiohttp.ClientSession() as session:
        result = await fetch(session, 'https://www.gaming.gen.tr/kategori/hazir-sistemler')
        soup = bs4(result, features="html.parser")
        page_count_elements = soup.find_all('a', class_='page-numbers')
        page_count = page_count_elements[-2].text

        href_list = []
        for page_number in range(1, int(page_count)+1):
            retries = 0
            while retries < 3:
                try:
                    result = await fetch(session, f'https://www.gaming.gen.tr/kategori/hazir-sistemler/page/{page_number}')
                    soup = bs4(result, features="html.parser")
                    product_list = soup.find('ul', class_='products columns-3').find_all('a')
                    for element in product_list:
                        href_list.append(element.get('href'))
                    break
                except Exception as e:
                    retries += 1
                    print(f'Retry {retries} for page {page_number} due to {e}')
            print('GaminggenTR at page, ', page_number)
        print(f'Found {len(href_list)} products in Gaming Gen Tr')
        return href_list


async def check_gaminggentr_details(href_list,dict_start_count,dict_end_count):
    """Create dictionary of all of the available pc's details
        :returns
    products dict [main product_name]
    products dict has 1 dict, image, main_link and price tag
    Inside dict has [product_category] = [product_title]
"""

    products = {}
    async with aiohttp.ClientSession() as session:
        for href in href_list[dict_start_count:dict_end_count]:
            retries = 0
            while retries < 3:
                try:
                    product_dict = {}

                    result = await fetch(session, href)
                    soup = bs4(result, features="html.parser")
                    main_title = soup.find('h1', class_='product_title entry-title').text.strip()
                    print(main_title)
                    image = soup.find(class_='woocommerce-product-gallery__image').find('img').get('data-src')
                    print(image)
                    price = soup.find('ins').find(class_='woocommerce-Price-amount amount').text.strip().replace('.',
                                                                                                                 '').split(
                        ",")
                    price = price[0]
                    print(price)

                    table_rows = soup.find(class_='su-table su-table-responsive su-table-alternate').find_all('tr')
                    for row in table_rows[1:]:
                        row = row.find_all('td')
                        product_category = row[0].text.strip().lower()
                        product_name = row[1].text.strip()
                        if product_category == 'bilgisayar kasaları':
                            product_category = 'kasa'
                        elif product_category == 'sıvı soğutucu':
                            product_category = 'soğutucu'
                        elif product_category == 'ram bellek':
                            product_category = 'ram'
                        elif product_category == 'güç kaynağı':
                            product_category = 'güç'

                        product_dict[product_category] = product_name
                    for key, value in product_dict.items():
                        print(f'{key}: {value}')
                    print(dict_start_count)
                    print(' ')
                    products[main_title] = [product_dict, image, href, price]
                    break
                except Exception as e:
                    retries += 1
                    print(f'Retry {retries} for page due to {e}')
    return products


async def get_gaminggentr_products():
    links = await get_gaminggentr_products_links()
    tasks = [
        check_gaminggentr_details(links, 0, 55),
        check_gaminggentr_details(links, 55, 110),
        check_gaminggentr_details(links, 110, 165),
        check_gaminggentr_details(links, 165, 220),
        check_gaminggentr_details(links, 220, None)

    ]
    results = await asyncio.gather(*tasks)
    product_dict_1, product_dict_2, product_dict_3, product_dict_4, product_dict_5 = results
    product_dict_1.update(product_dict_2)
    product_dict_1.update(product_dict_3)
    product_dict_1.update(product_dict_4)
    product_dict_1.update(product_dict_5)
    all_products_dict = product_dict_1

    return all_products_dict