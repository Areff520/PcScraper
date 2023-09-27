import datetime
import sqlite3
import psycopg2 as psycopg2


def update_local_db(pc_dict):
    for key, values in pc_dict.items():
        name = key
        details = str(values[1])
        name_forimage = name.replace('/',',')
        image = f'pc_images/{name_forimage}.jpg'
        link = values [2]
        price = values[3]
        old_price = values[4]
        difference = values[5]
        added_date = datetime.datetime.now()

        site = 'None'
        if 'gaming.gen' in link:
            site = 'GamingGenTR'

    # Your Heroku DATABASE_URL
    DATABASE_URL = "postgres://username:password@host:port/dbname"

    # Connect to your PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO main_page_product (name, price, old_price, difference, image, added_date, details, link, site) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (name, price, old_price, difference, image, added_date, details, link, site))

    conn.commit()
    conn.close()


def update_postgres_db(pc_dict):
    """Updats db on heroku. If the new attributes name allready exists in name table, only the different values are updated."""


    for key, values in pc_dict.items():
        name = key
        details = str(values[1])
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

    conn.commit()
    conn.close()


