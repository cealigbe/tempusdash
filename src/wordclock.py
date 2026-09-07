#!/usr/bin/python3

"""
TEMPUS DASH WORD CLOCK DISPLAY SCRIPT
"""

import datetime
import logging
import sys
import pathlib
import json
import time

import lib.clock as clock
from lib.render import *
from lib.datastore import DataStore


from PIL import Image
from configr import config
from utils import *

REFRESH_FACTOR = 10
REFRESH_INTERVAL = 10

if __name__ == '__main__':
    # clean up GPIO before starting
    cleanup_gpio()

    timestart = time.time()
    logger = logging.getLogger('tempusdash')

    tempus_path = config['tempus_folder']

    # rendered image dimensions and rotation angle
    img_w: int = config['img_width']
    img_h: int = config['img_height']
    angle: int = config['rotate_angle']
    # server_image_path = f"{tempus_path}/{config['wordclock_image_path']}"

    datastore = f"{tempus_path}/{config['data_store']}"

    # create and configure logger
    logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
    logger = logging.getLogger('tempusdash')
    logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
    logger.setLevel(logging.INFO)
    logger.info("Starting word clock update")

    # get date and year progress

    the_date = clock.get_date()
    the_time = clock.get_time()

    now = datetime.datetime.now()

    ctx = {
        'the_date': the_date,
        'the_time': the_time
    }

    renderer = RenderHelper(img_w, img_h, angle, "wordclock")
    process_template(ctx, "wordclock-template.jinja", "wordclock.html")

    renderedpath = renderer.get_screenshot()

    # send rendered image to epaper display

    ds = DataStore(datastore, flag='c')

    refresh_count = ds['refresh_count']

    if ds["current_app"] != "wordclock":
        updated = send_to_display(renderedpath, mode="full")
        refresh_count = 0
        ds['refresh_count'] = refresh_count
        ds.sync()
    elif refresh_count % REFRESH_INTERVAL == 0:
        updated = send_to_display(renderedpath, mode="full")
    else:
        updated = send_to_display(renderedpath, mode="fast")

    # update refresh count and timestamp in datastore
    if updated:
        logger.info("Word clock image displayed on screen")
        ds['refresh_count'] = refresh_count + 1
        ds.sync()

        timepassed = time.time() - timestart
        time.sleep(0.5)
        logger.info(f"Update complete. Time to update: {round(timepassed, 2)} seconds")

        ds['current_app'] = "wordclock"
        ds['timestamp'] = now.timestamp()
        ds.sync()

        update_history("wordclock", now.timestamp())

    else:
        logger.warning("Word clock image display failed")

    ds.close()
