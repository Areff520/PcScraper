import psycopg2
import requests
from PIL import Image
from io import BytesIO
import boto3
import os

def download_and_resize_image(image_url, new_dimensions=(220, 200)):

    # Download the image using requests
    response = requests.get(image_url)
    response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code

    # Use BytesIO to convert the response content into a streamable byte format
    image_stream = BytesIO(response.content)

    # Open, resize, and save the image using Pillow
    with Image.open(image_stream) as img:
        img_resized = img.resize(new_dimensions)
        if 'sinerji' in image_url:
            padding_sides = 60
            padding_top = 10
            padded_img = Image.new("RGB",
                                  (new_dimensions[0] + 2*padding_sides, new_dimensions[1] + padding_top),
                                  (255, 255, 255))
            padded_img.paste(img_resized, (padding_sides, padding_top))
        else:
            padded_img = img_resized

        buffer = BytesIO()
        padded_img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

def save_to_s3(file_buffer,name):

    name_forimage = name.replace('/', ',')

    # Initialize the S3 client
    s3 = boto3.client('s3')

    # Upload the file
    s3.upload_fileobj(file_buffer, 'enhesaplipc', f'pc_images/{name_forimage}.png')

def check_file_exists(file_key):
    """Deprecated-Checks if sing  file exists in S3 bucket"""

    s3 = boto3.client('s3')

    try:
        s3.head_object(Bucket='enhesaplipc', Key=file_key)
        return False
    except s3.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the file does not exist.
        if e.response['Error']['Code'] == "404":
            return True
def list_image_names():
    # Create an S3 client
    s3 = boto3.client('s3')

    # Create a reusable Paginator
    paginator = s3.get_paginator('list_objects_v2')

    # Create a PageIterator from the Paginator
    page_iterator = paginator.paginate(Bucket='enhesaplipc')

    files = []
    for page in page_iterator:
        if "Contents" in page:
            for key in page['Contents']:
                files.append(key['Key'])
    return files



def add_image(image_url,name):
    name_forimage = name.replace('/', ',')
    buffered_image = download_and_resize_image(image_url=image_url)
    save_to_s3(buffered_image, name)
    print('Image uploaded succesfully')



def remove_image():
    """Not being used"""
    s3 = boto3.client('s3')

    DATABASE_URL = os.environ.get('HEROKU_DB_URL')
    # Connect to your PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    query = "SELECT name FROM main_page_product"
    cursor.execute(query)
    rows= cursor.fetchall()
    db_name_list = []
    for row in rows:
        row = row[0].replace('/', ',')
        db_name_list.append(row)

    objects = s3.list_objects_v2(Bucket='enhesaplipc', Prefix='pc_images/')

    if 'Contents' in objects:
        for obj in objects['Contents']:
            # Get the object key, remove the folder name and '.png' extension to compare with the names in the dictionary
            object_key_without_extension = obj['Key'][len('pc_images/'):].rsplit('.', 1)[0]

            # If the name is not in the dictionary, delete the object from the bucket
            if object_key_without_extension not in db_name_list:
                print(f"Deleting {obj['Key']}")
                s3.delete_object(Bucket='enhesaplipc', Key=obj['Key'])