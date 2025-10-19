#!/usr/bin/python3

import logging
import sys
import pathlib
import time
import datetime
import json

from PIL import Image

from waveshare_epd import epd7in5_V2
from clock.clock import ClockModule
from render.render import WordclockRenderer

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

	# rendered image width, height, angle
	imgWidth = config['imgWidth']
	imgHeight = config['imgHeight']
	rotateAngle = config['rotateAngle']
	server_image_path = tempusPath + "/" + config['wordclock_image_path']

	manage_store = tempusPath + "/" + config['manage_store']

	# create and configure logger
	logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
	logger = logging.getLogger('tempusdash')
	logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
	logger.setLevel(logging.INFO)
	logger.info("Starting clock update")

	# get date and time
	clockMod = ClockModule()
	the_time = clockMod.get_time()
	the_date = clockMod.get_date()

	now = datetime.datetime.now()

	# render the wordclock image
	renderService = WordclockRenderer(imgWidth, imgHeight, rotateAngle)
	renderService.process_datetime(the_date, the_time, server_image_path)

	clockimage = Image.open(server_image_path)
	clockimage = clockimage.convert("1")

	minute_flap = {
			"xstart": 336,
			"ystart": 194,
			"xend": 336 + 312,
			"yend": 194 + 88
	}

	is_refresh_time = now.minute % 10 == 0
	with open(manage_store, "r") as storefile:
		storedict = json.load(storefile)

	is_not_running = storedict["name"] != "Wordclock"
	is_stale = (now.timestamp() - storedict["timestamp"])/60 >= 10

	if is_refresh_time or is_stale or is_not_running:
		epd.init()
		epd.Clear()
		epd.display(epd.getbuffer(clockimage))

		message = "Clock image refreshed on screen"
	else:
		epd.init_part()
		epd.display_Partial(epd.getbuffer(clockimage), minute_flap["xstart"], minute_flap["ystart"], minute_flap["xend"], minute_flap["yend"])

		message = "Clock minute updated on screen"

	logger.info(message)

	time.sleep(2)
	epd.sleep()

	logger.info("Completed clock update")

	manage_out = {
			"timestamp": now.timestamp(),
			"last_run": now.strftime("%B %d, %Y @ %H:%M"),
			"name": "Wordclock"
	}

	with open(manage_store, "w") as storefile:
		json.dump(manage_out, storefile, indent=4)
