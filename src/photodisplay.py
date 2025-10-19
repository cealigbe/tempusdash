#!/usr/bin/python3

import logging
import sys
import pathlib
import time
import datetime
import json

from PIL import Image

from waveshare_epd import epd7in5_V2
from config import config
from utils import *

if __name__ == '__main__':
	# Clean up GPIO before starting
	cleanup_gpio()

	logger = logging.getLogger('tempusdash')

	# load configuration for photo display
	tempusPath = config["TEMPUS_FOLDER"]

	# initialize display
	epd = epd7in5_V2.EPD()

	photo_path = tempusPath + "/" + config["photo_path"]
	error_photo = tempusPath + "/" + config["error_photo"]
	manage_store = tempusPath + "/" + config["manage_store"]

	# create and configure logger
	logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
	logger = logging.getLogger('tempusdash')
	logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
	logger.setLevel(logging.INFO)
	logger.info("Starting photo display")

	# get picture
	if pathlib.Path(photo_path).exists():
		is_displayed = send_to_display(photo_path, False)
		log_msg = "Photo suscessfully displayed on screen"
	else:
		is_displayed = send_to_display(error_photo, False)
		log_msg = "Photo not found"

	if is_displayed:
		logger.info(log_msg)
		time.sleep(0.5)
		logger.info("Completed photo display update")
	else:
		logger.info("Error: photo display failed")

	now = datetime.datetime.now()

	manage_out = {
	    "timestamp": now.timestamp(),
	    "last_run": now.strftime("%B %d, %Y @ %H:%M"),
			"name": "Photo Display"
	}

	with open(manage_store, "w") as storefile:
		json.dump(manage_out, storefile, indent=4)
