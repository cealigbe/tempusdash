"""
This script generates a HTML file of the dashboard to display. Then it fires up a
headless Chrome instance, sized to the resolution of the eInk display and takes a screenshot.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from datetime import timedelta
from jinja2 import Environment, FileSystemLoader

import pathlib
import string
from PIL import Image
import logging
from selenium.webdriver.common.by import By

class RenderHelper:

	def __init__(self, width, height, angle=0):
		self.logger = logging.getLogger('tempusdash')
		self.currPath = str(pathlib.Path(__file__).parent.absolute())

		self.imgWidth = width
		self.imgHeight = height
		self.rotateAngle = angle

		self.outputImg = "dash.png"
		self.outputHtml = "dash.html"
		self.templateFile = "dashboard-template.jinja"

		self.htmlFile = 'file://' + self.currPath + '/' + self.outputHtml

	def set_viewport_size(self, driver):

		# get window size from driver
		current_window_size = driver.get_window_size()

		# get client window size from the html tag
		html = driver.find_element(By.TAG_NAME, 'html')
		inner_width = int(html.get_attribute('clientWidth'))
		inner_height = int(html.get_attribute("clientHeight"))

		target_width = self.imgWidth + (current_window_size['width'] - inner_width)
		target_height = self.imgHeight + (current_window_size['height'] - inner_height)

		driver.set_window_rect(
			width=target_width,
			height=target_height)


	def get_screenshot(self, server_image_path):
		opts = Options()
		opts.add_argument("--headless")
		opts.add_argument("--hide-scrollbars")
		opts.add_argument("--forece-device-scale-factor=1")

		driver = webdriver.Chrome(options=opts)
		self.set_viewport_size(driver)
		driver.get(self.htmlFile)

		sleep(1)

		driver.get_screenshot_as_file(self.currPath + '/' + self.outputImg)
		driver.get_screenshot_as_file(server_image_path)
		self.logger.info('Screenshot captured and saved to file.')

	def process_inputs(self, raw_date, time_pct, the_weather, the_forecast, server_image_path):

		# read html template
		env = Environment(loader=FileSystemLoader(self.currPath))
		template = env.get_template(self.templateFile)

		context = {
			'time_pct': time_pct,
			'the_date': raw_date,
			'current': the_weather,
			'forecast': the_forecast
		}

		# render template and write to file
		rendered = template.render(context)

		with open(self.currPath + '/' + self.outputHtml, 'w') as htmlFile:
			htmlFile.write(rendered)

		self.get_screenshot(server_image_path)



class WordclockRenderer(RenderHelper):
	def __init__(self, width, height, angle=0):
		super().__init__(width, height, angle)

		self.outputImg = "wordclock.png"
		self.outputHtml = "wordclock.html"
		self.templateFile = "wordclock-template.jinja"

		self.htmlFile = 'file://' + self.currPath + '/' + self.outputHtml

	def process_datetime(self, the_date, the_time, server_image_path):

		# read html template
		env = Environment(loader=FileSystemLoader(self.currPath))
		template = env.get_template(self.templateFile)

		context = {
			'the_time': the_time,
			'the_date': the_date
		}

		# render template and write to file
		rendered = template.render(context)

		with open(self.currPath + '/' + self.outputHtml, 'w') as htmlFile:
			htmlFile.write(rendered)

		self.get_screenshot(server_image_path)
