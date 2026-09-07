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

from utils import cleanup_gpio, send_to_display

from lib.render import *
from lib.datastore import DataStore

from PIL import Image
from configr import config
from utils import *

def display_message(message_html: str, font_size: int = 16):
    # clean up GPIO before starting
    cleanup_gpio()

    timestart = time.time()
    logger = logging.getLogger('tempusdash')

    tempus_path = config['tempus_folder']

    # rendered image dimensions and rotation angle
    img_w: int = config['img_width']
    img_h: int = config['img_height']
    angle: int = config['rotate_angle']
    # server_image_path = f"{tempus_path}/{config['qrcode_image_path']}"

    datastore = f"{tempus_path}/{config['data_store']}"

    # create and configure logger
    logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
    logger = logging.getLogger('tempusdash')
    logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
    logger.setLevel(logging.INFO)
    logger.info("Starting message display")

    now = datetime.datetime.now()

    ctx = {
        'html': message_html,
        'font_size': font_size
    }

    renderer = RenderHelper(img_w, img_h, angle, "textdisplay")
    process_template(ctx, "textdisplay-template.jinja", "textdisplay.html")

    renderedpath = renderer.get_screenshot()

    # send rendered image to epaper display

    ds = DataStore(datastore, flag='c')

    updated = send_to_display(renderedpath, mode="full")

    if updated:
        logger.info("Message image displayed on screen")

        timepassed = time.time() - timestart
        time.sleep(0.5)
        logger.info(f"Update complete. Time to update: {round(timepassed, 2)} seconds")

        ds['refresh_count'] = 0
        ds['current_app'] = "textdisplay"
        ds['timestamp'] = now.timestamp()
        ds.sync()

        update_history("textdisplay", now.timestamp())

    else:
        logger.warning("Message image failed to display")

    ds.close()
