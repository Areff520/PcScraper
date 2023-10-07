import requests
from PIL import Image
from io import BytesIO
import boto3

def download_and_resize_image(image_url, new_dimensions=(600, 600)):

    #Changing Image size for sinerji products:
    if 'sinerji' in image_url:
        new_dimensions = (300, 600)
    # Download the image using requests
    response = requests.get(image_url)
    response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code

    # Use BytesIO to convert the response content into a streamable byte format
    image_stream = BytesIO(response.content)

    # Open, resize, and save the image using Pillow
    with Image.open(image_stream) as img:
        img_resized = img.resize(new_dimensions)
        buffer = BytesIO()
        img_resized.save(buffer, format="JPEG")
        buffer.seek(0)
        return buffer


def save_to_s3(file_buffer,name):

    name_forimage = name.replace('/', ',')

    # Initialize the S3 client
    s3 = boto3.client('s3')

    # Upload the file
    s3.upload_fileobj(file_buffer, 'enhesaplipc', f'pc_images/{name_forimage}.jpg')

def check_file_exists(file_key):
    s3 = boto3.client('s3')

    try:
        s3.head_object(Bucket='enhesaplipc', Key=file_key)
        return False
    except s3.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the file does not exist.
        if e.response['Error']['Code'] == "404":
            return True




def add_image(image_url,name):
    name_forimage = name.replace('/', ',')
    status = check_file_exists(f'pc_images/{name_forimage}.jpg')
    if status:
        buffered_image = download_and_resize_image(image_url=image_url)
        save_to_s3(buffered_image, name)
        print('Image uploaded succesfully')
    else:
        print('Image allready uploaded')


def remove_image():
    s3 = boto3.client('s3')

    names = []
    for pc_dict in dictionary_list:
        names.append(list(pc_dict.keys())[0].replace('/', ','))
    names = tuple(names)

    objects = s3.list_objects_v2(Bucket='enhesaplipc', Prefix='pc_images/')

    if 'Contents' in objects:
        for obj in objects['Contents']:
            # Get the object key, remove the folder name and '.jpg' extension to compare with the names in the dictionary
            object_key_without_extension = obj['Key'][len('pc_images/'):].rsplit('.', 1)[0]

            # If the name is not in the dictionary, delete the object from the bucket
            if object_key_without_extension not in names:
                print(f"Deleting {obj['Key']}")
                s3.delete_object(Bucket='enhesaplipc', Key=obj['Key'])