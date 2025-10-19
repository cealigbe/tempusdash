"""
This is the utility to get the current date and time in words.
"""


import logging
import datetime
from math import floor

def num_to_words(n):
	ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
	teens = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
	tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']

	if n < 1 or n > 99:
		return str(n)

	if n < 10:
		return ones[n]

	if n < 20:
		return teens[n - 10]

	ten = floor(n / 10)
	one = n % 10

	if one == 0:
		return tens[ten]
	else:
		return tens[ten] + '-' + ones[one]

def ordinal(i):
	j = i % 10
	k = i % 100

	if j == 1 and k != 11:
		return str(i) + "st"

	if j == 2 and k != 12:
		return str(i) + "nd"

	if j == 3 and k != 13:
		return str(i) + "rd"

	return str(i) + "th"


class ClockModule(object):
	def __init__(self):
		self.logger = logging.getLogger('tempusdash')

	def get_raw_date(self):
		weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
		months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

		today = datetime.date.today()
		weekday = weekdays[today.weekday()]
		month = months[today.month - 1]

		return {"weekday": weekday, "day": str(today.day).zfill(2), "month": month, "year": today.year}

	def get_date(self):
		today = datetime.date.today()
		fulldate = today.strftime('%A, %B {dd}, %Y').replace("{dd}", ordinal(today.day))

		return fulldate

	def get_time(self):
		now = datetime.datetime.now()
		time = now.time()

		hh = time.hour
		mm = time.minute

		ampm = "p.m." if hh >= 12 else "a.m."  # set AM or PM

		hh = hh % 12
		hh = hh if hh > 0 else 12

		hours = num_to_words(hh)
		minutes = num_to_words(mm)

		if mm == 0:
			minutes = "o'clock"
		elif mm < 10:
			minutes = "o' " + minutes

		return [hours, minutes, ampm]

	def get_time_pct(self):
		now = datetime.datetime.now()
		time = now.time()

		hh = time.hour
		mm = time.minute

		current_minutes = hh * 60 + mm

		percent = current_minutes/1440 * 100

		return round(percent, 3)





"""
clockmod = ClockModule()
print(clockmod.get_raw_date())
print(clockmod.get_time_pct())
"""
