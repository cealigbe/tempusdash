#!/usr/bin/python3

import logging
import sys
import pathlib
import time
import datetime
import json

from PIL import Image

# from waveshare_epd import epd7in5_V2
from clock.clock import ClockModule
from render.render import ProgressRenderer

from config import config
from utils import *

if __name__ == '__main__':
	# Clean up GPIO before starting
	cleanup_gpio()

	logger = logging.getLogger('tempusdash')

	# load configuration for photo display
	tempusPath = config["TEMPUS_FOLDER"]

	# rendered image width, height, angle
	imgWidth = config['imgWidth']
	imgHeight = config['imgHeight']
	rotateAngle = config['rotateAngle']
	server_image_path = tempusPath + "/" + config['progress_image_path']

	manage_store = tempusPath + "/" + config['manage_store']

	# create and configure logger
	logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
	logger = logging.getLogger('tempusdash')
	logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
	logger.setLevel(logging.INFO)
	logger.info("Starting year progress update")

	# get date and year progress
	clockMod = ClockModule()
	the_date = clockMod.get_date()
	progress = clockMod.get_ytd()

	now = datetime.datetime.now()

	# render the wordclock image
	renderService = ProgressRenderer(imgWidth, imgHeight, rotateAngle)
	renderService.proceess_progress(progress["year"], the_date, progress["pct"], progress["current_day"], progress["total_days"], server_image_path)

	is_displayed = send_to_display(server_image_path, False)

	if is_displayed:
		message = "Year progress displayed"
	else:
		message = "Issue displaying year progress"

	logger.info(message)

	if is_displayed:
		time.sleep(0.5)
		logger.info("Completed clock update")

	manage_out = {
			"timestamp": now.timestamp(),
			"last_run": now.strftime("%B %d, %Y @ %H:%M"),
			"name": "Year-to-date Progress"
	}

	with open(manage_store, "w") as storefile:
		json.dump(manage_out, storefile, indent=4)
