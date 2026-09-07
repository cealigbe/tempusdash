"""
This is where we retrieve weather forecast from WeatherAPI. Before doing so, make sure you have both the
signed up for an WeatherAPI account and also obtained a valid API key that is specified in the config.json file.
"""

import pathlib
import logging
import requests
import json
import datetime


# get weather icon code from condition code

def get_weather_icon(code: int) -> int:

  code_icons = {
      1000: 113,  # Sunny/Clear
      1003: 116,  # Partly cloudy
      1006: 119,  # Cloudy
      1009: 122,  # Overcast
      1030: 143,  # Mist
      1036: 143,  # Smoky haze
      1063: 176,  # Patchy rain possible
      1066: 179,  # Patchy snow possible
      1069: 182,  # Patchy sleet possible
      1072: 185,  # Patchy freezing drizzle possible
      1087: 200,  # Thundery outbreaks possible
      1114: 227,  # Blowing snow
      1117: 230,  # Blizzard
      1135: 248,  # Fog
      1147: 260,  # Freezing fog
      1150: 263,  # Patchy light drizzle
      1153: 266,  # Light drizzle
      1168: 281,  # Freezing drizzle
      1171: 284,  # Heavy freezing drizzle
      1180: 293,  # Patchy light rain
      1183: 296,  # Light rain
      1186: 299,  # Moderate rain at times
      1189: 302,  # Moderate rain
      1192: 305,  # Heavy rain at times
      1195: 308,  # Heavy rain
      1198: 311,  # Light freezing rain
      1201: 314,  # Moderate or heavy freezing rain
      1204: 317,  # Light sleet
      1207: 320,  # Moderate or heavy sleet
      1210: 323,  # Patchy light snow
      1213: 326,  # Light snow
      1216: 329,  # Patchy moderate snow
      1219: 332,  # Moderate snow
      1222: 335,  # Patchy heavy snow
      1225: 338,  # Heavy snow
      1237: 350,  # Ice pellets
      1240: 353,  # Light rain shower
      1243: 356,  # Moderate or heavy rain shower
      1246: 359,  # Torrential rain shower
      1249: 362,  # Light sleet showers
      1252: 365,  # Moderate or heavy sleet showers
      1255: 368,  # Light snow showers
      1258: 371,  # Moderate or heavy snow showers
      1261: 374,  # Light showers of ice pellets
      1264: 377,  # Moderate or heavy showers of ice pellets
      1273: 386,  # Patchy light rain with thunder
      1276: 389,  # Moderate or heavy rain with thunder
      1279: 392,  # Patchy light snow with thunder
      1282: 395   # Moderate or heavy snow with thunder
  }

  return code_icons[code]


# convert ISO date to weekday for forecast

def convert_date(date):
  weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  dd = datetime.date.fromisoformat(date)
  day = weekdays[dd.weekday()]

  return day

# Get current weather from WeatherAPI.com

def get_current_weather(location: str, apikey: str):
  url = f"http://api.weatherapi.com/v1/forecast.json?key={apikey}&q={location}&days=4&aqi=no&alerts=no"

  try:
    response = requests.get(url, timeout=15)
    data = json.loads(response.text)
  except requests.exceptions.Timeout:
    return {}

  # return empty dict in case of error
  if "error" in [*data]:
    return {}

  # extract weather data from response into a dict

  weather = {
      "location": data["location"]["name"],
      "region": data["location"]["region"],
      "country": data["location"]["country"],
      "text": data["current"]["condition"]["text"],
      "code": data["current"]["condition"]["code"],
      "is_day": data["current"]["is_day"],
      "temp": round(data["current"]["temp_f"]),
      "high": round(data["forecast"]["forecastday"][0]["day"]["maxtemp_f"]),
      "low": round(data["forecast"]["forecastday"][0]["day"]["mintemp_f"]),
  }

  weather["icon"] = get_weather_icon(weather["code"])
  weather["day_night"] = ['night', 'day'][weather["is_day"]]

  return weather

# get two-day forecast

def get_forecast(location: str, apikey: str):
  url = f"http://api.weatherapi.com/v1/forecast.json?key={apikey}&q={location}&days=7"

  try:
    response = requests.get(url, timeout=15)
    data = json.loads(response.text)
  except requests.exceptions.Timeout:
    return {}

  # return empty dict if there is an error in the response
  if "error" in [*data]:
    return {}

  # extract forecast data from response into a list of dicts
  forecast_data = data["forecast"]["forecastday"][1:3]
  forecast = []
  for dd in forecast_data:
    day = {
        "date": dd['date'],
        "weekday": convert_date(dd['date']),
        "text": dd['day']['condition']['text'],
        "code": dd['day']['condition']['code'],
        "high": round(dd['day']['maxtemp_f']),
        "low": round(dd['day']['mintemp_f'])
    }

    day["icon"] = get_weather_icon(day["code"])
    forecast.append(day)

  return forecast

# get hourly forecast

def get_hourly(location: str, apikey: str):
  url = f"http://api.weatherapi.com/v1/forecast.json?key={apikey}&q={location}&days=1"

  try:
    response = requests.get(url, timeout=15)
    data = json.loads(response.text)
  except requests.exceptions.Timeout:
    return {}

  # return empty dict if there is an error in the response
  if "error" in [*data]:
    return {}

  # extract hourly forecast data from response into a list of dicts
  hourlist = [8, 13, 18, 23]
  time_of_day = [("morn", "Morning"), ("noon", "Noon"), ("even", "Evening"), ("night", "Night")]
  today = data["forecast"]["forecastday"][0]["hour"]
  forecast_data = []

  for hourcast in today:
    hour = datetime.datetime.fromisoformat(hourcast['time']).hour

    if hour in hourlist:
      forecast_data.append(hourcast)

    forecast = []

    # build hourly forecast from forecast data
    for hf in forecast_data:
      hourly = {
          "hour": datetime.datetime.fromisoformat(hf["time"]).hour,
          "daytime": time_of_day[forecast_data.index(hf)],
          "text": hf['condition']['text'],
          "code": hf['condition']['code'],
          "temp": round(hf['temp_f'])
      }

      hourly["icon"] = get_weather_icon(hourly["code"])

      forecast.append(hourly)

  return forecast
