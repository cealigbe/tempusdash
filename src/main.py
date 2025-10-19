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

from utils import cleanup_gpio

from clock.clock import ClockModule
from weather.weather import WeatherModule
from render.render import RenderHelper

from PIL import Image
from config import config
from waveshare_epd import epd7in5_V2
from utils import *

if __name__ == '__main__':
	# clean up GPIO before starting
	cleanup_gpio()

	timestart = time.time()
	logger = logging.getLogger('tempusdash')

	tempusPath = config['TEMPUS_FOLDER']

	# initialize display
	epd = epd7in5_V2.EPD()

	# rendered image width, height, angle
	imgWidth = config['imgWidth']
	imgHeight = config['imgHeight']
	rotateAngle = config['rotateAngle']
	server_image_path = tempusPath + "/" + config['dashboard_image_path']

	# connect to Weather API
	location = config['location']
	apikey = config['apikey']
	weather_store = tempusPath + "/" + config['weather_store']
	error_store = tempusPath + "/" + config['error_store']
	manage_store = tempusPath + "/" + config['manage_store']

	# create and configure logger
	logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
	logger = logging.getLogger('tempusdash')
	logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
	logger.setLevel(logging.INFO)
	logger.info("Starting dashboard update")


	#get weather data, first look for the weather store
	if pathlib.Path(weather_store).exists():
		with open(weather_store, "r") as storefile:
			store = json.load(storefile)

		now = datetime.datetime.now()
		the_timestamp = now.timestamp()
		timediff = (the_timestamp - store["timestamp"])/60

		# pull weather data from WeatherAPI every 30 minutes
		if timediff >= 29:
			weatherMod = WeatherModule()
			the_weather = weatherMod.get_current_weather(location, apikey)
			the_forecast = weatherMod.get_hourly(location, apikey)

			weather_log = "Weather data downloaded"

			# check for errors from data download
			if len([*the_weather]) == 0 or len([*the_forecast]) == 0 :
				with open(error_store, "r") as errorfile:
					errordict = json.load(errorfile)

				the_timestamp = errordict["timestamp"]
				the_weather = errordict["weather"]
				the_forecast = errordict["forecast"]

				weather_log = "Weather data download failed"

			weatherout = {"timestamp": the_timestamp, "weather": the_weather, "forecast": the_forecast}

			with open(weather_store, "w") as storefile:
				json.dump(weatherout, storefile)

			logger.info(weather_log)

		# pull weather data from store before 30 minutes have passed
		else:
			the_weather = store["weather"]
			the_forecast = store["forecast"]

	#get weather data from web if there is no store and then save it
	else:
		now = datetime.datetime.now()
		the_timestamp = now.timestamp()

		weatherMod = WeatherModule()
		the_weather = weatherMod.get_current_weather(location, apikey)
		the_forecast = weatherMod.get_hourly(location, apikey)

		weather_log = "Weather data downloaded"

		# check for errors from data download
		if len([*the_weather]) == 0 or len([*the_forecast]) == 0 :
			with open(error_store, "r") as errorfile:
				errordict = json.load(errorfile)

			the_timestamp = errordict["timestamp"]
			the_weather = errordict["weather"]
			the_forecast = errordict["forecast"]

			weather_log = "Weather data download failed"

		weatherout = {"timestamp": the_timestamp, "weather": the_weather, "forecast": the_forecast}

		with open(weather_store, "w") as storefile:
			json.dump(weatherout, storefile, indent=4)

		logger.info(weather_log)

	# retreive date and time
	clockMod = ClockModule()
	raw_date = clockMod.get_raw_date()
	time_pct = clockMod.get_time_pct()

	# render dashboard image
	renderService = RenderHelper(imgWidth, imgHeight, rotateAngle)
	renderService.process_inputs(raw_date, time_pct, the_weather, the_forecast, server_image_path)

	#display dashboard image
	dashimage = Image.open(server_image_path)
	dashimage = dashimage.convert("1")


	epd.init()
	epd.Clear()
	epd.display(epd.getbuffer(dashimage))


	logger.info("Dashboard image displayed on screen")

	time.sleep(2)
	epd.sleep()

	timepassed = time.time() - timestart

	logger.info("Completed dashboard update")
	logger.info("Time to update: {:.2f} seconds".format(timepassed))

	manage_out = {
	    "timestamp": now.timestamp(),
			"last_run": now.strftime("%B %d, %Y @ %H:%M"),
			"name": "Time Weather Dashboard"
	}

	with open(manage_store, "w") as storefile:
		json.dump(manage_out, storefile, indent=4)
