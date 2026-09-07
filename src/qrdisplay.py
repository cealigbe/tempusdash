#!/usr/bin/python3

"""
TEMPUS DASH QR CODE DISPLAY SCRIPT

This script is a simple utility that displays a QR code on the screen.
The QR code is generated via the Tempus Dash Manager.
"""

import datetime
import logging
import sys
import pathlib
import json
import time

from utils import cleanup_gpio, send_to_display

from lib.qrencoder import *
from lib.render import *
from lib.datastore import DataStore

from PIL import Image
from configr import config
from utils import *

def display_qr(title: str, data: str, description:str|None=None, showdata: bool = True):
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
    logger.info("Starting QR code display")

    qr_code = encode_qr_base64(data)
    qr_url = f"data:image/png;base64,{qr_code}"

    now = datetime.datetime.now()

    ctx = {
        'title': title,
        'data': data,
        'description': description,
        'showdata': showdata,
        'qrcode_url': qr_url
    }

    renderer = RenderHelper(img_w, img_h, angle, "qrcode")
    process_template(ctx, "qrcode-template.jinja", "qrcode.html")

    renderedpath = renderer.get_screenshot()

    # send rendered image to epaper display

    ds = DataStore(datastore, flag='c')

    updated = send_to_display(renderedpath, mode="full")

    if updated:
        logger.info("QR code image displayed on screen")

        timepassed = time.time() - timestart
        time.sleep(0.5)
        logger.info(f"Update complete. Time to update: {round(timepassed, 2)} seconds")

        ds['refresh_count'] = 0
        ds['current_app'] = "qrcode"
        ds['timestamp'] = now.timestamp()
        ds.sync()

        update_history("qrcode", now.timestamp())

    else:
        logger.warning("QR code image failed to display")

    ds.close()

"""
if __name__ == "__main__":
    display_qr("My website", "https://www.chuck.aligbe.com", "This is the description of my website. The QR code is displayed on the screen.", showdata=False)
"""
