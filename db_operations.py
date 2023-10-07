import datetime
import sqlite3
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
                popped_key, popped_value = pc_dict.popitem()
                popped_key_list.append(popped_key)
                price_didnot_change[popped_key] = popped_value
                print(f'POPPED {name}  {price}')
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
def update_postgres_db(pc_dict):
    """Updats db on heroku. If the new attributes name allready exists in name table, only the different values are updated."""


    for key, values in pc_dict.items():
        name = key
        details = str(values[0])
        name_forimage = name.replace('/',',')
        image = f'pc_images/{name_forimage}.jpg'
        link = values[2]
        price = values[3]
        old_price = values[4]
        difference = values[5]
        added_date = datetime.datetime.now()

        site = 'None'
        if 'gaming.gen' in link:
            site = 'GamingGenTR'
        elif 'itopya' in link:
            site = 'Itopya'
        elif 'sinerji' in link:
            site = 'Sinerji'
        elif 'pckolik' in link:
            site = 'PcKolik'

    # Your Heroku DATABASE_URL
    DATABASE_URL = "postgres://ebaexwhefvudks:15aa66769709ff3f5fc34eb86f34a17ae0b536ccb487f7717882ded07a0b23c3@ec2-34-254-138-204.eu-west-1.compute.amazonaws.com:5432/d9l42cr2ekv8cn"

    # Connect to your PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    # SQL query with ON CONFLICT for upsert operation
    cursor.execute('''
    INSERT INTO main_page_product (name, price, old_price, difference, image, added_date, details, link, site) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (name)
    DO UPDATE SET 
        price = EXCLUDED.price,
        old_price = EXCLUDED.old_price,
        difference = EXCLUDED.difference,
        image = EXCLUDED.image,
        details = EXCLUDED.details,
        link = EXCLUDED.link,
        site = EXCLUDED.site;
    ''', (name, price, old_price, difference, image, added_date, details, link, site))

    cursor.execute('''
    WITH cte AS (	
  SELECT id,
         ROW_NUMBER() OVER (PARTITION BY name ORDER BY id) AS rn
    FROM main_page_productdetails
)
DELETE FROM main_page_productdetails WHERE id IN (SELECT id FROM cte WHERE rn > 1);
''')
    cursor.execute(populate_main_page_productdetails)

    conn.commit()
    conn.close()

def delete_rows(dictionary_list, price_didnot_change_dict):
    """Deletes the row that do not contain the name in the dictionary. These rows are old and outdated

    Takes:
    list
    dict
    """
    names = []
    for pc_dict in dictionary_list:
        names.append(list(pc_dict.keys())[0])
    for key, value in price_didnot_change_dict.items():
        names.append(key)
    names = tuple(names)


    DATABASE_URL = "postgres://ebaexwhefvudks:15aa66769709ff3f5fc34eb86f34a17ae0b536ccb487f7717882ded07a0b23c3@ec2-34-254-138-204.eu-west-1.compute.amazonaws.com:5432/d9l42cr2ekv8cn"

    # Connect to your PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    query = sql.SQL("DELETE FROM main_page_product WHERE name NOT IN %s")
    cursor.execute(query, (names,))
    conn.commit()
    conn.close()

def check_if_same_exists_postgres(pc_dict):
    """Deprecated -Connects to PostgreSQL to check if the products exists and price is same,
     if yes pops the item from pd_dict"""

    DATABASE_URL = "postgres://ebaexwhefvudks:15aa66769709ff3f5fc34eb86f34a17ae0b536ccb487f7717882ded07a0b23c3@ec2-34-254-138-204.eu-west-1.compute.amazonaws.com:5432/d9l42cr2ekv8cn"

    # Connect to your PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    query = "SELECT name, price FROM main_page_product"
    cursor.execute(query)
    rows= cursor.fetchall()
    product_dict_copy = pc_dict.copy()
    print(len (pc_dict))
    for title, values in product_dict_copy.items():
        price = int(values[3])

        for row in rows:
            if title == row[0] and price-1000< row[1] < price+1000:
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

populate_main_page_productdetails = '''
INSERT INTO main_page_productdetails  (name, gpu_model, cpu_model, product_id)
SELECT 
    name,
    CASE 
        WHEN POSITION('rtx 4090' IN LOWER(details)) > 0 OR POSITION('rtx 4090' IN LOWER(name)) > 0 THEN 'RTX 4090'
        WHEN POSITION('rtx 4080' IN LOWER(details)) > 0 OR POSITION('rtx 4080' IN LOWER(name)) > 0 THEN 'RTX 4080'
        WHEN POSITION('rtx 4070 ti' IN LOWER(details)) > 0 OR POSITION('rtx 4070 ti' IN LOWER(name)) > 0 THEN 'RTX 4070 TI'
        WHEN POSITION('rtx 4070 ' IN LOWER(details)) > 0 OR POSITION('rtx 4070 ' IN LOWER(name)) > 0 THEN 'RTX 4070'
        WHEN POSITION('rtx 4060 ti' IN LOWER(details)) > 0 OR POSITION('rtx 4060 ti' IN LOWER(name)) > 0 THEN 'RTX 4060 TI'
        WHEN POSITION('rtx 4060' IN LOWER(details)) > 0 OR POSITION('rtx 4060' IN LOWER(name)) > 0 THEN 'RTX 4060'
        WHEN POSITION('rtx 4050' IN LOWER(details)) > 0 OR POSITION('rtx 4050' IN LOWER(name)) > 0 THEN 'RTX 4050'
        WHEN POSITION('rtx 3090 ti' IN LOWER(details)) > 0 OR POSITION('rtx 3090 ti' IN LOWER(name)) > 0 THEN 'RTX 3090 TI'
        WHEN POSITION('rtx 3090' IN LOWER(details)) > 0 OR POSITION('rtx 3090' IN LOWER(name)) > 0 THEN 'RTX 3090'
        WHEN POSITION('rtx 3080 ti' IN LOWER(details)) > 0 OR POSITION('rtx 3080 ti' IN LOWER(name)) > 0 THEN 'RTX 3080 TI'
        WHEN POSITION('rtx 3080' IN LOWER(details)) > 0 OR POSITION('rtx 3080' IN LOWER(name)) > 0 THEN 'RTX 3080'
        WHEN POSITION('rtx 3070 ti' IN LOWER(details)) > 0 OR POSITION('rtx 3070 ti' IN LOWER(name)) > 0 THEN 'RTX 3070 TI'
        WHEN POSITION('rtx 3070 ' IN LOWER(details)) > 0 OR POSITION('rtx 3070 ' IN LOWER(name)) > 0 THEN 'RTX 3070'
        WHEN POSITION('rtx 3060 ti' IN LOWER(details)) > 0 OR POSITION('rtx 3060 ti' IN LOWER(name)) > 0 THEN 'RTX 3060 TI'
        WHEN POSITION('rtx 3060' IN LOWER(details)) > 0 OR POSITION('rtx 3060' IN LOWER(name)) > 0 THEN 'RTX 3060'
        WHEN POSITION('rtx 3050' IN LOWER(details)) > 0 OR POSITION('rtx 3050' IN LOWER(name)) > 0 THEN 'RTX 3050'
        WHEN POSITION('rx 7900 xtx' IN LOWER(details)) > 0 OR POSITION('rx 7900 xtx' IN LOWER(name)) > 0 THEN 'RX 7900 XTX'
        WHEN POSITION('rx 7900 xt' IN LOWER(details)) > 0 OR POSITION('rx 7900 xt' IN LOWER(name)) > 0 THEN 'RX 7900 XT'
        WHEN POSITION('rx 7800 xt' IN LOWER(details)) > 0 OR POSITION('rx 7800 xt' IN LOWER(name)) > 0 THEN 'RX 7800 XT'
        WHEN POSITION('rx 7700 xt' IN LOWER(details)) > 0 OR POSITION('rx 7700 xt' IN LOWER(name)) > 0 THEN 'RX 7700 XT'
        WHEN POSITION('rx 7600' IN LOWER(details)) > 0 OR POSITION('rx 7600' IN LOWER(name)) > 0 THEN 'RX 7600'
        WHEN POSITION('rx 6950 xt' IN LOWER(details)) > 0 OR POSITION('rx 6950 xt' IN LOWER(name)) > 0 THEN 'RX 6950 XT'
        WHEN POSITION('rx 6900 xt' IN LOWER(details)) > 0 OR POSITION('rx 6900 xt' IN LOWER(name)) > 0 THEN 'RX 6900 XT'
        WHEN POSITION('rx 6850 xt' IN LOWER(details)) > 0 OR POSITION('rx 6850 xt' IN LOWER(name)) > 0 THEN 'RX 6850 XT'
        WHEN POSITION('rx 6800' IN LOWER(details)) > 0 OR POSITION('rx 6800' IN LOWER(name)) > 0 THEN 'RX 6800'
        WHEN POSITION('rx 6750 xt' IN LOWER(details)) > 0 OR POSITION('rx 6750 xt' IN LOWER(name)) > 0 THEN 'RX 6750 XT'
        WHEN POSITION('rx 6700 xt' IN LOWER(details)) > 0 OR POSITION('rx 6700 xt' IN LOWER(name)) > 0 THEN 'RX 6700 XT'
        WHEN POSITION('rx 6650 xt' IN LOWER(details)) > 0 OR POSITION('rx 6650 xt' IN LOWER(name)) > 0 THEN 'RX 6650 XT'
        WHEN POSITION('rx 6600 xt' IN LOWER(details)) > 0 OR POSITION('rx 6600 xt' IN LOWER(name)) > 0 THEN 'RX 6600 XT'
        WHEN POSITION('rx 6600' IN LOWER(details)) > 0 OR POSITION('rx 6600' IN LOWER(name)) > 0 THEN 'RX 6600'
        ELSE NULL 
    END as gpu_model,
    CASE 
        WHEN POSITION('intel core i5-13400f' IN LOWER(details)) > 0 
          OR POSITION('i5 13400f' IN LOWER(details)) > 0 THEN 'i5 13400F'
        WHEN POSITION('intel core i5-12400f' IN LOWER(details)) > 0 
          OR POSITION('i5 12400F' IN LOWER(details)) > 0 THEN 'i5 12400F'
        WHEN POSITION('intel core i3-12100f' IN LOWER(details)) > 0 
          OR POSITION('i3 12100F' IN LOWER(details)) > 0 THEN 'i3 12100F'
        WHEN POSITION('amd ryzen 5 5600' IN LOWER(details)) > 0 THEN 'Ryzen 5 5600'
        WHEN POSITION('amd ryzen 5 7500f' IN LOWER(details)) > 0 THEN 'Ryzen 5 7500F'
        WHEN POSITION('amd ryzen 5 5500' IN LOWER(details)) > 0 THEN 'Ryzen 5 5500'
        WHEN POSITION('intel core i9-13900k' IN LOWER(details)) > 0 
          OR POSITION('i9 13900' IN LOWER(details)) > 0 THEN 'i9 13900K'
        WHEN POSITION('amd ryzen 7 7800x3d' IN LOWER(details)) > 0 THEN 'Ryzen 7 7800X'
        WHEN POSITION('intel core i3-13100f' IN LOWER(details)) > 0 
          OR POSITION('i3 13100F' IN LOWER(details)) > 0 THEN 'i3 13100F'
        WHEN POSITION('ryzen 5' IN LOWER(details)) > 0 THEN 'Ryzen 5'
        WHEN POSITION('ryzen 7' IN LOWER(details)) > 0 THEN 'Ryzen 7'
        ELSE NULL 
    END as cpu_model,
    name
FROM main_page_product 
WHERE 
    POSITION('rtx 4090' IN LOWER(details)) > 0 
    OR POSITION('rtx 4080' IN LOWER(details)) > 0 
    OR POSITION('rtx 4070 ti' IN LOWER(details)) > 0 
    OR POSITION('rtx 4070 ' IN LOWER(details)) > 0 
    OR POSITION('rtx 4060 ti' IN LOWER(details)) > 0 
    OR POSITION('rtx 4060' IN LOWER(details)) > 0 
    OR POSITION('rtx 4050' IN LOWER(details)) > 0 
    OR POSITION('rtx 3090 ti' IN LOWER(details)) > 0 
    OR POSITION('rtx 3090' IN LOWER(details)) > 0 
    OR POSITION('rtx 3080 ti' IN LOWER(details)) > 0 
    OR POSITION('rtx 3080' IN LOWER(details)) > 0 
    OR POSITION('rtx 3070 ti' IN LOWER(details)) > 0 
    OR POSITION('rtx 3070 ' IN LOWER(details)) > 0 
    OR POSITION('rtx 3060 ti' IN LOWER(details)) > 0 
    OR POSITION('rtx 3060' IN LOWER(details)) > 0 
    OR POSITION('rtx 3050' IN LOWER(details)) > 0
    OR POSITION('rx 7900 xtx' IN LOWER(details)) > 0
    OR POSITION('rx 7900 xt' IN LOWER(details)) > 0
    OR POSITION('rx 7800 xt' IN LOWER(details)) > 0
    OR POSITION('rx 7700 xt' IN LOWER(details)) > 0
    OR POSITION('rx 7600' IN LOWER(details)) > 0
    OR POSITION('rx 6950 xt' IN LOWER(details)) > 0
    OR POSITION('rx 6900 xt' IN LOWER(details)) > 0
    OR POSITION('rx 6850 xt' IN LOWER(details)) > 0
    OR POSITION('rx 6800' IN LOWER(details)) > 0
    OR POSITION('rx 6750 xt' IN LOWER(details)) > 0
    OR POSITION('rx 6700 xt' IN LOWER(details)) > 0
    OR POSITION('rx 6650 xt' IN LOWER(details)) > 0
    OR POSITION('rx 6600 xt' IN LOWER(details)) > 0
    OR POSITION('rx 6600' IN LOWER(details)) > 0
    OR POSITION('ryzen 5' IN LOWER(details)) > 0
    OR POSITION('ryzen 7' IN LOWER(details)) > 0;;
    --Deleting duplicates
DELETE FROM main_page_productdetails
WHERE id IN (
    SELECT id FROM (
        SELECT id, 
               ROW_NUMBER() OVER (PARTITION BY name ORDER BY id) AS rnum
         FROM main_page_productdetails
    ) t
    WHERE t.rnum > 1
);
    '''