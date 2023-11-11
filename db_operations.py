import datetime
import sqlite3
import traceback
import os
import psycopg2 as psycopg2
from psycopg2 import sql


def update_local_db(pc_dict):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    print(len(pc_dict))
    popped_key_list = []
    price_didnot_change = {}
    product_dict_copy = pc_dict.copy()
    for key, values in product_dict_copy.items():
        name = key
        price = float(values[3])

        cursor.execute('SELECT price FROM main_page_product WHERE name=?', (name,))
        row = cursor.fetchone()

        if row is not None:
            existing_price = row[0]
            if abs(existing_price - price) >= 1000:
                cursor.execute('''
                    UPDATE main_page_product
                    SET price=?
                    WHERE name=?
                ''', (price, name))
                print(f"Updated {name} to {price}")
            else:
                popped_key, popped_value = pc_dict.popitem(key)
                popped_key_list.append(popped_key)
                price_didnot_change[popped_key] = popped_value
                print(f'POPPED')
        else:
            cursor.execute('''
                INSERT INTO main_page_product (name, price)
                VALUES (?, ?)
            ''', (name, price))
            print(f"Inserterd {name}  {price}")

        conn.commit()

    # Delete rows where the name is not in pc_dict keys
    key_list = list(pc_dict.keys())
    key_list += popped_key_list
    names_tuple = tuple(key_list)
    placeholders = ', '.join('?' for _ in names_tuple)  # Create placeholders for the names
    query = f'''
        DELETE FROM main_page_product WHERE name NOT IN ({placeholders})
    '''
    cursor.execute(query, names_tuple)


    conn.commit()
    conn.close()

    return pc_dict, price_didnot_change
def populate_main_page_product_db(key, values):
    """Updats db on heroku. If the new attributes name allready exists in name table, only the different values are updated."""

    name = key
    details = str(values[0])
    name_forimage = name.replace('/',',')
    image = f'pc_images/{name_forimage}.png '
    link = values[2]
    price = values[3]
    if len(values) == 6:
        old_price = values[4]
        difference = values[5]
    else:
        old_price = 1
        difference = 1
    added_date = datetime.datetime.now()
    is_stock_available = True
    site = 'None'
    if 'gaming.gen' in link:
        site = 'GamingGenTR'
    elif 'itopya' in link:
        site = 'Itopya'
    elif 'sinerji' in link:
        site = 'Sinerji'
    elif 'pckolik' in link:
        site = 'PcKolik'
    elif 'gamegara' in link:
        site = 'GameGaraj'

    # Your Heroku DATABASE_URL
    DATABASE_URL = os.environ.get('HEROKU_DB_URL')

    # Connect to your PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    if int(price) > 10000 and difference > -50:

        # SQL query with ON CONFLICT for upsert operation
        cursor.execute('''
        INSERT INTO main_page_product (name, price, old_price, difference, image, added_date, details, link, site, is_stock_available) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (name)
        DO UPDATE SET 
            price = EXCLUDED.price,
            old_price = EXCLUDED.old_price,
            difference = EXCLUDED.difference,
            image = EXCLUDED.image,
            details = EXCLUDED.details,
            link = EXCLUDED.link,
            site = EXCLUDED.site,
            is_stock_available = EXCLUDED.is_stock_available;
        ''', (name, price, old_price, difference, image, added_date, details, link, site, is_stock_available))

    elif difference < -50:
        cursor.execute('''
        INSERT INTO exception_products (name, price, old_price, difference, image, added_date, details, link, site) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (name, price, old_price, difference, image, added_date, details, link, site))

        difference = 50
        cursor.execute('''
        INSERT INTO main_page_product (name, price, old_price, difference, image, added_date, details, link, site, is_stock_available) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (name)
        DO UPDATE SET 
            price = EXCLUDED.price,
            old_price = EXCLUDED.old_price,
            difference = EXCLUDED.difference,
            image = EXCLUDED.image,
            details = EXCLUDED.details,
            link = EXCLUDED.link,
            site = EXCLUDED.site,
            is_stock_available = EXCLUDED.is_stock_available;

        ''', (name, price, old_price, difference, image, added_date, details, link, site, is_stock_available))
    conn.commit()
    conn.close()

def change_is_stock_available(all_products_dict):
    """Change the row that do not contain the name in the dictionary. These rows are old and outdated, so the stock set to False
    Website will not display these rows
    Takes:
    list
    dict
    """
    names = []
    for key, value in all_products_dict.items():
        names.append(key)
    names = tuple(names)


    DATABASE_URL = os.environ.get('HEROKU_DB_URL')

    # Connect to your PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    query = sql.SQL("UPDATE main_page_product SET is_stock_available = %s WHERE name NOT IN %s")
    cursor.execute(query, (False, names))
    conn.commit()
    conn.close()

def check_if_same_exists_postgres(pc_dict):
    """Deprecated -Connects to PostgreSQL to check if the products exists and price is same and difference is positive
     value, pops the item from pc_dict"""

    DATABASE_URL = os.environ.get('HEROKU_DB_URL')

    # Connect to your PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    query = "SELECT name, price, difference FROM main_page_product"
    cursor.execute(query)
    rows = cursor.fetchall()
    product_dict_copy = pc_dict.copy()
    print(len (pc_dict))

    for title, values in product_dict_copy.items():
        price = int(values[3])
        for row in rows:
            if title == row[0] and price-1000 < row[1] < price+1000 or row[2] > -5 and title == row[0]:
                pc_dict.pop(title)
    print(f'Removed {len(product_dict_copy) - len(pc_dict)} items from the dict because their price have not changed yet')
    conn.close()

    return pc_dict

def check_if_same_exists_local(pc_dict):
    """ this is not working properly with other db operations. Popped items no bueno """
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    product_dict_copy = pc_dict.copy()
    for title, values in product_dict_copy.items():
        price = int(values[3])
        cursor.execute('SELECT price FROM main_page_product WHERE name = ?', (title,))
        row = cursor.fetchone()
        if row:
            if row[0] == price or row[0] + 1000 < price < row[0] + 1000:
                print('POPPED')
                pc_dict.pop(title)
            else:
                cursor.execute('UPDATE main_page_product SET price = ? WHERE name = ?', (price, title))
                print(f"Updated {title} to {price}")
    conn.close()
    return pc_dict

def take_all_name_values():
    """Not used atm """
    DATABASE_URL = os.environ.get('HEROKU_DB_URL')

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    select_query = """
    SELECT name
    FROM main_page_product
    """
    cur.execute(select_query)
    name_values = cur.fetchall()
    name_values = [row[0] for row in name_values]

    return name_values

def populate_main_product_details_db(tuple_list):
    DATABASE_URL = os.environ.get('HEROKU_DB_URL')
    print('Populating main_page_productdetails')
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    query = """
    INSERT INTO main_page_productdetails (product_id, name_shortened, cpu_shortened, cpu_model, gpu_shortened, gpu_model, motherboard_shortened, motherboard_model, 
    ram_shortened, ram_speed, ram_capacity, ssd_shortened, ssd_capacity)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (product_id)
    DO UPDATE SET 
        name_shortened = EXCLUDED.name_shortened, 
        cpu_shortened = EXCLUDED.cpu_shortened, 
        cpu_model = EXCLUDED.cpu_model, 
        gpu_shortened = EXCLUDED.gpu_shortened, 
        gpu_model = EXCLUDED.gpu_model, 
        motherboard_shortened = EXCLUDED.motherboard_shortened, 
        motherboard_model = EXCLUDED.motherboard_model, 
        ram_shortened = EXCLUDED.ram_shortened, 
        ram_speed = EXCLUDED.ram_speed, 
        ram_capacity = EXCLUDED.ram_capacity, 
        ssd_shortened = EXCLUDED.ssd_shortened, 
        ssd_capacity = EXCLUDED.ssd_capacity
   """

    for item in tuple_list:
        try:
            cur.execute(query, item)
            conn.commit()
            print('Inserted Succesfully')
        except psycopg2.errors.ForeignKeyViolation:
            print(f"Failed to insert {item} due to foreign key violation.")
            conn.rollback()  # Important: rollback the transaction after an error
            continue  # Skip this item and proceed to the next one
        except Exception as e:
            print(item)
            traceback.print_exc()

            print(f"An error occurred: {e}")
            conn.rollback()  # Rollback the transaction after an error
            continue  # Skip this item and proceed to the next one
    cur.execute('''
        WITH cte AS (	
      SELECT id,
             ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY id) AS rn
        FROM main_page_productdetails
    )
    DELETE FROM main_page_productdetails WHERE id IN (SELECT id FROM cte WHERE rn > 1);
    ''')

    conn.commit()
    cur.close()
    conn.close()

def temp_fix_column(pc_dicts):
    """temporary code to fix image column"""
    for key, values in pc_dicts.items():
        name = key
        name_forimage = name.replace('/',',')
        image = f'pc_images/{name_forimage}.jpg'
        print(image)


        # Your Heroku DATABASE_URL
        DATABASE_URL = os.environ.get('HEROKU_DB_URL')

        # Connect to your PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()

        # SQL query with ON CONFLICT for upsert operation
        cursor.execute('''
            UPDATE main_page_product 
            SET image = %s 
            WHERE name = %s;
            ''', (image, name))
        print('INSERTED')
        conn.commit()
    conn.close()
