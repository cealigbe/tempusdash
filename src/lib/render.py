"""
This script generates a HTML file of the dashboard to display. Then it fires up a
headless Chrome instance, sized to the resolution of the eInk display and takes a screenshot.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep
from datetime import timedelta
from jinja2 import Environment, FileSystemLoader

import pathlib
import os
import shutil
import logging
from selenium.webdriver.common.by import By

LIB_DIR = str(pathlib.Path(__file__).parent.absolute())
TEMPLATE_DIR = LIB_DIR + "/templates"
TEMPUS_DIR = str(pathlib.Path(__file__).parent.parent.absolute())
RENDER_DIR = TEMPUS_DIR + "/render"

# processes a Tempus template and saves the HTML output to the render directory
def process_template(ctx, template_file: str, output_file: str):
    if not os.path.exists(RENDER_DIR):
        os.makedirs(RENDER_DIR)

    shutil.copy(TEMPLATE_DIR + "/style.css", RENDER_DIR + "/style.css")
    shutil.copytree(TEMPLATE_DIR + "/font", RENDER_DIR + "/font", dirs_exist_ok=True)
    shutil.copytree(TEMPLATE_DIR + "/icons", RENDER_DIR + "/icons", dirs_exist_ok=True)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(template_file)
    output = template.render(ctx)

    with open(RENDER_DIR + "/" + output_file, 'w') as f:
        f.write(output)

# helper class for rendering screenshots from Tempus templates
class RenderHelper:
    def __init__(self, width: int, height: int, angle=0, filename=""):
        self.logger = logging.getLogger("tempusdash")

        self.img_w: int = width
        self.img_h: int = height
        self.angle: int = angle
        self.filename: str = filename

        self.htmlFile: str = f"file:///{RENDER_DIR}/{self.filename}.html"

    def set_viewport_size(self, driver):
        # set the window size to the image size
        window_size = driver.get_window_size()

        html = driver.find_element(By.TAG_NAME, 'html')
        inner_w = int(html.get_attribute('clientWidth'))
        inner_h = int(html.get_attribute('clientHeight'))

        target_w = self.img_w + (window_size['width'] - inner_w)
        target_h = self.img_h + (window_size['height'] - inner_h)

        driver.set_window_rect(0, 0, target_w, target_h)

    def get_screenshot(self):
        # create a screenshot of the rendered template using a headless Chrome instance
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--hide-scrollbars')
        opts.add_argument("--force-device-scale-factor=1")

        opts.binary_location = "/usr/bin/chromium-browser"

        service = Service(executable_path="/usr/bin/chromedriver")

        renderedpath = None

        driver = webdriver.Chrome(options=opts, service=service)
        self.set_viewport_size(driver)
        try:
            driver.get(self.htmlFile)

            sleep(1)

            renderedpath = f"{RENDER_DIR}/{self.filename}.png"
            driver.get_screenshot_as_file(renderedpath)
            self.logger.info(f"Screenshot captured and saved to {renderedpath}")
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot: {e}")
            raise
        finally:
            driver.quit()

        return renderedpath
