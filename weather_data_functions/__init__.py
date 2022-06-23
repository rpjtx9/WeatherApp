import os
import requests
from datetime import datetime

from flask import (
    request
)

class WeatherInfo:
    @staticmethod
    def map_entry(entry):
        if isinstance(entry, dict):
            return WeatherInfo(**entry)
        return entry
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if type(val) == dict:
                setattr(self, key, WeatherInfo(**val))
            elif type(val) == list:
                setattr(self, key, list(map(self.map_entry, val)))
            else:
                setattr(self, key, val)

def weather_lookup(lat, lon, units="imperial"):
    """Takes the latitude and longitude of a location and returns weather data at that location. Defaults to imperial units, standard and metric are alternative options"""
    # Call the API
    try:
        api_key = "211bb8b91bce61229a97d7fc04d2dcbb"       #os.environ.get("API_KEY") having a hard time with this at the moment
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units={units}&appid={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    
    # Parse out json
    try:
        rawdata = response.json()
        weather = WeatherInfo(**rawdata)
        return weather

    except (KeyError, TypeError, ValueError):
        return None