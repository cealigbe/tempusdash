"""
This is the utility to get the current date and time in words.
"""


import datetime
from math import floor


# converts a number to words for a word clock
def num_to_words(n: int):
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

# converts a number to its ordinal representation
def ordinal(i: int):
    j = i % 10
    k = i % 100

    if j == 1 and k != 11:
        return str(i) + "st"

    if j == 2 and k != 12:
        return str(i) + "nd"

    if j == 3 and k != 13:
        return str(i) + "rd"

    return str(i) + "th"

# returns the raw date as a dictionary
def get_raw_date():
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    today = datetime.date.today()
    weekday = weekdays[today.weekday()]
    month = months[today.month - 1]

    return {"weekday": weekday, "day": str(today.day).zfill(2), "month": month, "year": today.year}

# returns the full date as a string with the day in ordinal form
def get_date():
    today = datetime.date.today()
    fulldate = today.strftime('%A, %B {dd}, %Y').replace("{dd}", ordinal(today.day))

    return fulldate

# returns the year-to-date progress as a dictionary
def get_ytd():
    today = datetime.date.today()
    start_day = datetime.date(today.year, 1, 1)
    end_day = datetime.date(today.year, 12, 31)
    total_days = (end_day - start_day).days + 1
    doyr = (today - start_day).days + 1
    progress_pct = (doyr / total_days) * 100

    year_to_date = {
            "year": today.year,
            "total_days": total_days,
            "current_day": doyr,
            "pct": progress_pct
    }

    return year_to_date

# returns the current time as a list of words
def get_time():
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

# returns the current time as a percentage of the day
def get_time_pct():
    now = datetime.datetime.now()
    time = now.time()

    hh = time.hour
    mm = time.minute

    current_minutes = hh * 60 + mm

    percent = current_minutes / 1440 * 100

    return round(percent, 3)
