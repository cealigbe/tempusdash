#!/usr/bin/python3

"""
TEMPUS DASH WEATHER DISPLAY SCRIPT

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
import lib.weather as weather
from lib.render import *
from lib.datastore import DataStore


from PIL import Image
from configr import config
from utils import *

ERROR_JSON = """
{"weather":{"location":"New York City","region":"New York","text":"Error","code":9999,"icon":"error","is_day":1,"day_night":"day","temp":"--","high":"--","low":"--"},"forecast":[{"hour":8,"daytime":["morn","Morning"],"text":"Error","code":9999,"temp":"--","icon":"error"},{"hour":13,"daytime":["noon","Noon"],"text":"Error","code":9999,"temp":"--","icon":"error"},{"hour":18,"daytime":["even","Evening"],"text":"Error","code":9999,"temp":"--","icon":"error"},{"hour":23,"daytime":["night","Night"],"text":"Error","code":9999,"temp":"--","icon":"error"}]}
"""

REFRESH_FACTOR = 10
REFRESH_INTERVAL = 5

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
    server_image_path = f"{tempus_path}/{config['dashboard_image_path']}"

    # connect to WeatherAPI
    location: str = config['location']
    apikey: str = config['apikey']
    datastore = f"{tempus_path}/{config['data_store']}"

    # create and configure logger
    logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
    logger = logging.getLogger('tempusdash')
    logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
    logger.setLevel(logging.INFO)
    logger.info("Starting Tempus dashboard update")

    # get weatehr data
    now = datetime.datetime.now()

    the_weather = weather.get_current_weather(location, apikey)
    the_forecast = weather.get_hourly(location, apikey)

    weatherlog: str = "Weather data updated"

    # check if weather data is valid
    if len([*the_weather]) == 0 or len([*the_forecast]) == 0:
        errordict = json.loads(ERROR_JSON)

        the_weather = errordict['weather']
        the_forecast = errordict['forecast']

        weatherlog = "Weather data update failed"

    ds = DataStore(datastore, flag='c')
    ds['weather'] = the_weather
    ds['forecast'] = the_forecast
    ds.sync()

    logger.info(weatherlog)

    # get data and time
    raw_date = clock.get_raw_date()
    time_pct = clock.get_time_pct()

    # render dashboard image
    ctx = {
        'time_pct': time_pct,
        'the_date': raw_date,
        'current': the_weather,
        'forecast': the_forecast
    }

    renderer = RenderHelper(img_w, img_h, angle, "dash")
    process_template(ctx, "dashboard-template.jinja", "dash.html")

    renderedpath = renderer.get_screenshot()

    # send rendered image to epaper display

    refresh_count = ds['refresh_count']

    if ds["current_app"] != "tempus":
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
        logger.info("Dashboard image displayed on screen")
        ds['refresh_count'] = refresh_count + 1
        ds.sync()

        timepassed = time.time() - timestart
        time.sleep(0.5)
        logger.info(f"Update complete. Time to update: {round(timepassed, 2)} seconds")

        ds['current_app'] = "tempus"
        ds['timestamp'] = now.timestamp()
        ds.sync()

        update_history("tempus", now.timestamp())

    else:
        logger.warning("Dashboard image display failed")

    ds.close()
