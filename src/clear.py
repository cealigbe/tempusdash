# Simple clear function and script
from utils import *

def clear():
  cleanup_gpio()

  from waveshare_epd import epd7in5_V2

  epd = epd7in5_V2.EPD()

  epd.init()
  epd.Clear()
  epd.sleep()

  cleanup_gpio()
  return True

if __name__ == '__main__':
  clear()
