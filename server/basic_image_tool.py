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


def download_image(url, filename):
    # Get Image
    if not os.path.exists("images"):
        os.mkdir("images")
    else:
        pass
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

            return base_url, image_name, nasa_date


def backfill_images(length=48):
    base_url, starting_filename, extracted_tstamp = get_latest_image(
        bypass=True)
    files_list = list_generator(
        base_url, starting_filename, extracted_tstamp, length)

    for image_url in files_list:
        image_name = image_url.split('/')[-1]
        if download_image(image_url, image_name):
            continue
        else:
            if os.path.exists(image_name):
                print("Unable to download because we already have the image.")
                continue
            else:
                print(f"Unable to download {image_url}")
                continue

    return True


def create_video_loop(length=48):
    # Create temp directory
    if os.path.isdir(os.path.join(os.path.curdir, "temp")):
        pass
    else:
        os.mkdir("temp")

    # Rename files
    file_name_list = os.listdir("./images")

    new_count = 0
    print("Re-naming files...")
    for file_name in sorted(file_name_list):
        if ".jpg" not in file_name:
            continue
        new_count += 1
        os.rename(os.path.abspath(os.path.join(os.path.curdir, "images", file_name)), os.path.abspath(
            os.path.join(os.path.curdir, "images", "img{:03d}.jpg".format(new_count))))

    # Process w/ FFMPEG
    print("Generating video loop...")
    movie_name = "test_video.mp4"
    logger.info("Beginning FFMPEG encode...")
    with open("./logfile.log", "a") as output:
        try:
            subprocess.check_call(
                """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -y -stats -framerate 8 -i images/img%03d.jpg -c:v libx264 -vf scale=2048:-1 -pix_fmt yuv420p temp/{}""".format(movie_name),
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

    # Try to remove tree; if failed show an error using try...except on screen
    try:
        print("Cleaning up imagery directory...")
        shutil.rmtree("images")
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
    backfill_images(length=144)
    create_video_loop(length=144)
