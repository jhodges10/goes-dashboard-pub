import time
import traceback
from datetime import timedelta, datetime
import random
import subprocess
import shutil
import os
import sys
import traceback
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
import urllib.request
import requests
from bs4 import BeautifulSoup as BS
from models import database, create_tables, Media, Image
from settings import logger, q, redis_conn

nasa_page = "https://www.star.nesdis.noaa.gov/GOES/fulldisk.php?sat=G17"


def get_page(url=nasa_page):
    page = requests.get(url)
    page_source = page.content
    return page_source


def process_html(html):
    geo_color_urls = list()

    soup = BS(html, 'html.parser')
    link_source = soup.find_all(class_='FB')

    for url in link_source:
        if "GeoColor" in url.attrs['title']:
            geo_color_urls.append(url.attrs['href'])
        else:
            pass

    for url in geo_color_urls:
        if "5424" in url:
            return url


def upload_to_s3(file_path, file_name, mime_type, replace=True):
    print(f"Uploading: {file_name}")
    bucket_name = 'sat-images'
    ACCESS_KEY = 'minio'
    SECRET_KEY = 'minio123'

    minioClient = Minio("localhost:9000",
                        access_key=ACCESS_KEY,
                        secret_key=SECRET_KEY,
                        secure=False)

    # Make a bucket with the make_bucket API call.
    try:
        minioClient.make_bucket(bucket_name)
    except BucketAlreadyOwnedByYou as err:
        pass
    except BucketAlreadyExists as err:
        pass
    except ResponseError as err:
        raise

    try:
        minioClient.fput_object(bucket_name, file_name,
                                file_path, content_type=mime_type)
        print(f"Upload complete for: {file_name}")
        try:
            presigned_url = minioClient.presigned_url(
                'GET', bucket_name, file_name, expires=(timedelta(days=7)))
            logger.info(f"Pre-signed URL generated: {presigned_url}")
            return presigned_url
        except Exception as err:
            logger.info(f"Failed to generate URL")
            logger.error(err)
    except Exception as err:
        logger.error(err)
        logger.error("Exiting...")


def download_image(url, filename):
    # Get Image
    fullfilename = os.path.join("images", filename)
    if os.path.exists(fullfilename):
        logger.info('File already exists: {}'.format(filename))
        return False
    try:
        logger.info('Downloading image from url: {}'.format(url))
        urllib.request.urlretrieve(url, fullfilename)
        logger.info("Image download complete for: {}".format(filename))
        return True
    except PermissionError:
        logger.info("We already have this image: {}".format(filename))
        return False
    except urllib.error.HTTPError:
        logger.info("This URL is no good: {}".format(url))
        return False


def get_latest_image(bypass=False):
    page_data = get_page()
    image_url = process_html(page_data)
    image_name = image_url.split("/")[-1]
    base_url = 'https://cdn.star.nesdis.noaa.gov/GOES17/ABI/FD/GEOCOLOR/'

    if bypass:
        nasa_date = datetime.strptime(image_name.split("_")[0], "%Y%j%H%M")
        return base_url, image_name, nasa_date

    else:
        # Check to see if file already exists
        if image_name in os.listdir('images'):
            print("Image already exists, aborting.")
            return None

        else:
            if download_image(image_url, image_name):
                pass

            # Convert NASA Date to datetime.datetime
            nasa_date = datetime.strptime(image_name.split("_")[0], "%Y%j%H%M")

            # Upload and get URL
            try:
                presigned_url = upload_to_s3(
                    f"images/{image_name}", image_name, "image/jpeg")
                create_tables()
                Image.insert(
                    {
                        "media_type": "image",
                        "name": image_name,
                        "original_url": image_url,
                        "s3_id": image_name,
                        "nasa_date": nasa_date,
                        "presigned_url": presigned_url,
                    }
                ).on_conflict_ignore().execute()
                print("Saved to S3 and stored in the database")

            except Exception as e:
                print(e)
                print("Failed to upload image to S3")
                sys.exit(1)

            return base_url, image_name, nasa_date


# A simple function to use requests.post to make the API call. Note the json= section.
def run_query(query):
    print("Running Query")
    request = requests.post(
        "http://localhost:8080/v1/graphql", json={'query': query})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(
            request.status_code, query))


def backfill_images(length=48):
    base_url, starting_filename, extracted_tstamp = get_latest_image(
        bypass=True)
    files_list = list_generator(
        base_url, starting_filename, extracted_tstamp, length)

    for image_url in files_list:
        image_name = image_url.split('/')[-1]
        if download_image(image_url, image_name):
            pass
        else:
            continue

        # Convert NASA Date to datetime.datetime
        nasa_date = datetime.strptime(image_name.split("_")[0], "%Y%j%H%M")

        # Upload and get URL
        try:
            presigned_url = upload_to_s3(
                f"images/{image_name}", image_name, "image/jpeg")
            create_tables()
            Image.insert(
                {
                    "media_type": "image",
                    "name": image_name,
                    "original_url": image_url,
                    "s3_id": image_name,
                    "nasa_date": nasa_date,
                    "presigned_url": presigned_url,
                }
            ).on_conflict_ignore().execute()
            print("Saved to S3 and stored in the database")

        except Exception as e:
            print(e)
            print("Failed to upload image to S3")
            sys.exit(1)


def create_video_loop(length=48):
    # Create temp directory
    if os.path.isdir(os.path.join(os.path.curdir, "temp")):
        pass
    else:
        os.mkdir("temp")

    # Get last 48 images
    query = """
        {
            image(distinct_on: nasa_date, order_by: {nasa_date: desc}, limit: {length}) {
                original_url
                nasa_date
                date_added
                s3_id
                name
            }
        }
    """.replace("{length}", f"{length}")
    result = run_query(query)['data']['image']
    logger.info(f"GraphQL returned {len(list(result))} records")

    # Init Minio
    ACCESS_KEY = 'minio'
    SECRET_KEY = 'minio123'

    minioClient = Minio("localhost:9000",
                        access_key=ACCESS_KEY,
                        secret_key=SECRET_KEY,
                        secure=False)

    # Download images
    try:
        for image in result:
            logger.info(f"Downloading: {image['s3_id']}")
            minioClient.fget_object(
                'sat-images', image['s3_id'], f"./temp/{image['name']}")
    except PermissionError:
        logger.error(r"Ran into permission error I guess ¯\_(ツ)_/¯")

        # Delete temp directory
        os.system("rm -r temp/")
        shutil.rmtree("temp")

        # Create temp directory
        if os.path.isdir(os.path.join(os.path.curdir, "temp")):
            pass
        else:
            os.mkdir("temp")

        for image in result:
            logger.info(f"Downloading: {image['s3_id']}")
            minioClient.fget_object(
                'sat-images', image['s3_id'], f"./temp/{image['name']}")

    # Rename files
    file_name_list = os.listdir("./temp")

    new_count = 0
    print("Re-naming files...")
    for file_name in sorted(file_name_list):
        if ".jpg" not in file_name:
            continue
        new_count += 1
        os.rename(os.path.abspath(os.path.join(os.path.curdir, "temp", file_name)), os.path.abspath(
            os.path.join(os.path.curdir, "temp", "img{:03d}.jpg".format(new_count))))

    # Process w/ FFMPEG
    print("Generating video loop...")
    movie_name = "test_video.mp4"
    logger.info("Beginning FFMPEG encode...")
    with open("./logfile.log", "a") as output:
        try:
            subprocess.check_call(
                """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -stats -framerate 8 -i temp/img%03d.jpg -c:v libx264 -vf scale=2048:-1 -pix_fmt yuv420p temp/{}""".format(movie_name),
                shell=True, stdout=output, stderr=output
            )
        except subprocess.CalledProcessError as e:
            print(e)
            # Try to remove tree; if failed show an error using try...except on screen
            try:
                shutil.rmtree("temp")
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
            sys.exit(1)

    # Wait a sec to make sure the video is ready
    time.sleep(2)

    # Delete old video
    minioClient.remove_object('sat-images', movie_name)

    # Upload and get URL
    print("Uploading video...")
    try:
        presigned_url = upload_to_s3(
            f"temp/{movie_name}", movie_name, "video/mp4")
        create_tables()
        Media.insert(
            {
                "media_type": "movie",
                "name": movie_name,
                "s3_id": movie_name,
                "presigned_url": presigned_url,
            }
        ).on_conflict_ignore().execute()

    except Exception as e:
        print("Failed to upload image to S3")
        print(e)

    # Try to remove tree; if failed show an error using try...except on screen
    try:
        shutil.rmtree("temp")
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

    return True


def list_generator(base_url, starting_filename, extracted_tstamp, length=48):
    """Returns the last 48 timestamps using timedelta
    """
    print(base_url)
    print(starting_filename)
    print(extracted_tstamp)

    url_list = list()

    for i in range(1, length):
        new_tstamp = extracted_tstamp - timedelta(minutes=(10*i))
        new_filename = f"""{datetime.strftime(new_tstamp, '%Y%j%H%M')}_{starting_filename.split('_')[1]}"""
        full_url = base_url + new_filename
        url_list.append(full_url)

    print(url_list)

    return url_list


if __name__ == "__main__":
    get_latest_image()
    create_video_loop()
    # backfill_images(length=144)
    # create_video_loop(length=144)
