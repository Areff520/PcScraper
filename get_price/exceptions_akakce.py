def exception_akakce(product_name, link='None', product_category='None', price=0, product_not_found = False):
    if 'rtx 4070 ti' in product_name:
        link = link.replace('&s=2', '')
        return product_name, link

    elif ' mpk' in product_name and product_category == 'i̇şlemci':
        product_name = product_name.replace(' mpk', '')
        return product_name, link

    if product_category == 'ssd' and price > 4000:
        if '1tb' in product_name:
            price = 2250
            return price
        elif '500' in product_name:
            price = 1000
            return price
    if product_not_found and 'pny rtx' in product_name:
        product_name_splitted = product_name.split(' ')
        product_name_for_link = ''
        for name in product_name_splitted[0:3]:
            product_name_for_link += f'{name}+'
        link = f'https://www.akakce.com/arama/?q={product_name_for_link}'
        return product_name, link
    return product_name, link

def check_price(status, price_per_item, total_price):
    if status:
        for category, item_price in price_per_item.items():
            if 'ekran kartı' not in category and item_price * 3 > total_price:
                status = False
                return status


