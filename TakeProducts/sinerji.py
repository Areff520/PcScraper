import traceback
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
    async with session.get(url, headers=headers) as response:
        return await response.text()



async def get_sinerji_products_list():
    """Returns all of the listing in the website on list format"""

    product_href_list = []
    async with aiohttp.ClientSession() as session:
        try:
            result = await fetch(session, 'https://www.sinerji.gen.tr/oyun-bilgisayari-c-2116?sx=BestSellers')
            soup = bs4(result, features="html.parser")
            page_count = soup.find(class_='paging').find_all('a')
            page_count = page_count[-2].text.strip()

            tasks = []
            for page in range(1, int(page_count) + 1):
                url = f'https://www.sinerji.gen.tr/oyun-bilgisayari-c-2116?sx=BestSellers&px={page}'
                tasks.append(fetch(session, url))

            pages_content = await asyncio.gather(*tasks)
            for content in pages_content:
                soup = bs4(content, features="html.parser")
                product_list = soup.find_all(class_='col-xl-3')
                for product_wrapper in product_list:
                    link = product_wrapper.find('a').get('href')
                    product_href_list.append(link)

        except Exception as e:
            print(traceback.format_exc())
    return product_href_list


async def check_sinerji_details(href_list):
    """
        :returns
        products dict [main product_name]
        products dict has 1 dict and 1 image href inside, href  and 1 price tag
        Inside dict has products[product_category] = [product_title]

        """
    products = {}
    async with aiohttp.ClientSession() as session:
        for href in href_list:
            href = f'https://www.sinerji.gen.tr{href}'
            content = await fetch(session, href)
            try:
                soup = bs4(content, features="html.parser")
                main_title = soup.find('h1').get_text().strip()
                image = soup.find('a', class_='productPhotoCarouselPhotoLink').get('data-img')
                price = soup.find('span', class_='price').find('span').get_text().strip().replace('.', '').split(",")
                price = price[0]

                tables = soup.find_all(class_='row preBuiltPcCategory')
                product_dict = {}
                for table in tables[2:]:
                    product_category = table.find('h3').get_text().strip().lower()
                    rows = table.find_all(class_='preBuiltPcProduct')
                    for row in rows:
                        if row.get('data-isdefault') == 'true':
                            title_element = row.find('label')
                            product_title = title_element.get_text().strip().replace('ÖNERİLEN', '').replace('İNDİRİM',
                                                                                                             '').replace(
                                '\n', '')
                            if product_title.endswith("i"):
                                product_title = product_title[::-1].replace("i", "", 1)[::-1]
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
                        print('\n\n')
                        print(main_title)
                        for key, value in product_dict.items():
                            print(f'{key}: {value}')
            except Exception as e:
                print('Error occurred while processing href', href)
                print(traceback.format_exc())
    return products

async def get_sinerji_products():
    links = await get_sinerji_products_list()
    all_products_dict = await check_sinerji_details(links)
    return all_products_dict



