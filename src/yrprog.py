#!/usr/bin/python3

"""
This project is designed for the Waveshare 7.5 display. However, since the server code is only generating an image, it can
be easily adapted to other display sizes and resolution by adjusting the config settings, HTML template and
CSS stylesheet. This code is heavily adapted from MagInkDash by speedyg0nz. As a dashboard,
there are many other things that could be displayed, and it can be done as long as you are able to
retrieve the information. So feel free to change up the code and amend it to your needs.
"""

import datetime
import logging
import sys
import pathlib
import json
import time

from utils import cleanup_gpio, send_to_display

import lib.clock as clock
from lib.render import *
from lib.datastore import DataStore

from PIL import Image
from configr import config
from utils import *

REFRESH_FACTOR = 10
REFRESH_INTERVAL = 6

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
    # server_image_path = f"{tempus_path}/{config['progress_image_path']}"

    datastore = f"{tempus_path}/{config['data_store']}"

    # create and configure logger
    logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
    logger = logging.getLogger('tempusdash')
    logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
    logger.setLevel(logging.INFO)
    logger.info("Starting YTD progress update")

    # get date and year progress

    the_date = clock.get_date()
    progress = clock.get_ytd()

    now = datetime.datetime.now()

    ctx = {
        'year': progress['year'],
        'the_date': the_date,
        'pct': progress['pct'],
        'current_day': progress['current_day'],
        'total_days': progress['total_days']
    }

    renderer = RenderHelper(img_w, img_h, angle, "yearprogress")
    process_template(ctx, "yearprogress-template.jinja", "yearprogress.html")

    renderedpath = renderer.get_screenshot()

    # send rendered image to epaper display

    ds = DataStore(datastore, flag='c')

    refresh_count = ds['refresh_count']

    if ds["current_app"] != "yearprogress":
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
        logger.info("Year progress image displayed on screen")
        ds['refresh_count'] = refresh_count + 1
        ds.sync()

        timepassed = time.time() - timestart
        time.sleep(0.5)
        logger.info(f"Update complete. Time to update: {round(timepassed, 2)} seconds")

        ds['current_app'] = "yearprogress"
        ds['timestamp'] = now.timestamp()
        ds.sync()

        update_history("yearprogress", now.timestamp())

    else:
        logger.warning("Year progress image display failed")

    ds.close()
