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

def send_to_display(imagepath, grayscale=False):
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

    if grayscale:
      resimage = resimage.convert("L")

      epd.init_4Gray()
      epd.Clear()
      epd.display_4Gray(epd.getbuffer_4Gray(resimage))

    else:
      resimage = resimage.convert("1")

      epd.init()
      epd.Clear()
      epd.display(epd.getbuffer(resimage))

    time.sleep(2)
    epd.sleep()

    cleanup_gpio()

    return True

  except Exception as e:
    print(f"Photo display error: {e}")
    cleanup_gpio()
    return False

def imageurl_to_display(url, grayscale=False):
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

    if grayscale:
      resimage = resimage.convert("L")

      epd.init_4Gray()
      epd.Clear()
      epd.display_4Gray(epd.getbuffer_4Gray(resimage))

    else:
      resimage = resimage.convert("1")

      epd.init()
      epd.Clear()
      epd.display(epd.getbuffer(resimage))

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
