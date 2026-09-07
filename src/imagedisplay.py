#!/usr/bin/python3

"""
TEMPUS DASH MESSAGE DISPLAY SCRIPT

This script is a simple utility that displays a message on the screen.
"""

import datetime
import logging
import sys
import pathlib
import json
import time

from utils import cleanup_gpio, send_to_display, imageurl_to_display

from lib.render import *
from lib.datastore import DataStore

from PIL import Image
from configr import config
from utils import *

def display_image(imagepath: str):
    # clean up GPIO before starting
    cleanup_gpio()

    timestart = time.time()
    logger = logging.getLogger('tempusdash')

    tempus_path = config['tempus_folder']

    datastore = f"{tempus_path}/{config['data_store']}"

    # create and configure logger
    logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
    logger = logging.getLogger('tempusdash')
    logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
    logger.setLevel(logging.INFO)
    logger.info("Starting image display")

    now = datetime.datetime.now()

    # send image to epaper display

    ds = DataStore(datastore, flag='c')

    updated = send_to_display(imagepath, mode="full")

    if updated:
        logger.info(f"{imagepath} displayed on screen")

        timepassed = time.time() - timestart
        time.sleep(0.5)
        logger.info(f"Update complete. Time to update: {round(timepassed, 2)} seconds")

        ds['refresh_count'] = 0
        ds['current_app'] = "photodisplay"
        ds['timestamp'] = now.timestamp()
        ds.sync()

        update_history("photodisplay", now.timestamp())

    else:
        logger.warning("Image failed to display")

    ds.close()

def display_imageurl(url: str):
    # clean up GPIO before starting
    cleanup_gpio()

    timestart = time.time()
    logger = logging.getLogger('tempusdash')

    tempus_path = config['tempus_folder']

    datastore = f"{tempus_path}/{config['data_store']}"

    # create and configure logger
    logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
    logger = logging.getLogger('tempusdash')
    logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
    logger.setLevel(logging.INFO)
    logger.info("Starting image URL display")

    now = datetime.datetime.now()

    # send image to epaper display

    ds = DataStore(datastore, flag='c')

    updated = imageurl_to_display(url, mode="full")

    if updated:
        logger.info(f"{url} displayed on screen")

        timepassed = time.time() - timestart
        time.sleep(0.5)
        logger.info(f"Update complete. Time to update: {round(timepassed, 2)} seconds")

        ds['refresh_count'] = 0
        ds['current_app'] = "imgurldisplay"
        ds['timestamp'] = now.timestamp()
        ds.sync()

        update_history("imgurldisplay", now.timestamp())

    else:
        logger.warning("Image failed to display")

    ds.close()
