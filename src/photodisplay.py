#!/usr/bin/python3

"""
TEMPUS DASH SIMPLE PHOTO DISPLAY SCRIPT

This script is a simple utility that displays a preset photo on the screen.
"""


import logging
import sys
import pathlib
import time
import datetime
import json

from PIL import Image

from configr import config
from utils import *

from lib.datastore import DataStore

if __name__ == '__main__':
	# Clean up GPIO before starting
	cleanup_gpio()

	logger = logging.getLogger('tempusdash')

	# load configuration for photo display
	tempusPath = config["tempus_folder"]

	photo_path = tempusPath + "/" + config["photo_path"]
	error_photo = tempusPath + "/" + config["error_photo"]
	data_store = tempusPath + "/" + config["data_store"]

	# create and configure logger
	logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
	logger = logging.getLogger('tempusdash')
	logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
	logger.setLevel(logging.INFO)
	logger.info("Starting photo display")

	# get picture

	now = datetime.datetime.now()

	ds = DataStore(data_store, flag="c")

	if pathlib.Path(photo_path).exists():
		is_displayed = send_to_display(photo_path, "full")
		log_msg = "Photo suscessfully displayed on screen"
	else:
		is_displayed = send_to_display(error_photo, "full")
		log_msg = "Photo not found"

	if is_displayed:
		logger.info(log_msg)
		time.sleep(0.5)
		logger.info("Completed photo display update")

		ds['current_app'] = "photodisplay"
		ds['timestamp'] = now.timestamp()
		ds['refresh_count'] = 0
		ds.sync()

		update_history("photodisplay", now.timestamp())
	else:
		logger.info("Error: photo display failed")

	ds.close()
