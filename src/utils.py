#!/usr/bin/python3

"""
GPIO Wrapper Script
Handles GPIO operations in isolation to prevent conflicts
"""
import sys
import os
import time
import signal
import atexit

from configr import config

def cleanup_gpio():
    """Force cleanup of all GPIO resources"""
    try:
        import gpiozero
        if gpiozero.Device.pin_factory:
            gpiozero.Device.pin_factory.reset()
    except:
        pass

def signal_handler(signum, frame):
    """Handle termination signals"""
    cleanup_gpio()
    sys.exit(0)

def isclose(a, b, tol=0.01):
  epsilon = abs(a - b)
  return epsilon < tol

# Register cleanup handlers
atexit.register(cleanup_gpio)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def _full_update(epd, image):
  epd.init()
  epd.Clear()
  epd.display(epd.getbuffer(image))

def _grayscale_update(epd, image):
  epd.init_4Gray()
  epd.Clear()
  epd.display_4Gray(epd.getbuffer_4Gray(image))

def _fast_update(epd, image):
  epd.init_fast()
  epd.display(epd.getbuffer(image))

def send_to_display(imagepath, mode="full"):
  """ Send an image at specified location to the display """

  cleanup_gpio()

  try:
    from waveshare_epd import epd7in5_V2
    from PIL import Image, ImageOps

    epd = epd7in5_V2.EPD()

    if not os.path.exists(imagepath):
      return False

    image = Image.open(imagepath)
    resimage = ImageOps.pad(image, (epd.width, epd.height), color="white")

    if mode == "grayscale":
      resimage = resimage.convert("L")

      _grayscale_update(epd, resimage)

    elif mode == "fast":
      resimage = resimage.convert("1")
      _fast_update(epd, resimage)

    else:
      resimage = resimage.convert("1")

      _full_update(epd, resimage)

    time.sleep(2)
    epd.sleep()

    cleanup_gpio()

    return True

  except Exception as e:
    print(f"Photo display error: {e}")
    cleanup_gpio()
    return False

def imageurl_to_display(url, mode="full"):
  """ Send an image at specified URL to the display """

  cleanup_gpio()

  try:
    from waveshare_epd import epd7in5_V2
    from PIL import Image, ImageOps
    from io import BytesIO

    import requests

    epd = epd7in5_V2.EPD()

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
      print("Photo display error: Request failed")
      cleanup_gpio()
      return False

    urlfile = BytesIO(response.content)

    image = Image.open(urlfile)
    resimage = ImageOps.pad(image, (epd.width, epd.height), color="white")

    if mode == "grayscale":
      resimage = resimage.convert("L")

      _grayscale_update(epd, resimage)

    elif mode == "fast":
      resimage = resimage.convert("1")
      _fast_update(epd, resimage)

    else:
      resimage = resimage.convert("1")

      _full_update(epd, resimage)

    time.sleep(2)
    epd.sleep()

    cleanup_gpio()

    return True

  except Exception as e:
    print(f"Photo display error: {e}")
    cleanup_gpio()
    return False

def clear_display():
    """Clear the display"""
    cleanup_gpio()

    try:
      from waveshare_epd import epd7in5_V2

      epd = epd7in5_V2.EPD()

      epd.init()
      epd.Clear()
      epd.sleep()

      cleanup_gpio()

      return True

    except Exception as e:
      print(f"Clear display error: {e}")
      cleanup_gpio()
      return False

def update_history(app:str, timestamp:float, history_file:str=config["tempus_folder"] + "/" + config["history_file"]):
    """Log the app name and timestamp into the history file"""

    from datetime import datetime

    if not os.path.exists(history_file):
        with open(history_file, "w") as f:
            f.write("app,timestamp,datetime\n")

    with open(history_file, "a") as f:
        f.write(f"{app},{timestamp},{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
