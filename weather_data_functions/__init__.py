import os
import requests
from datetime import datetime

from flask import (
    current_app,
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

def weather_lookup(lat, lng, units="imperial"):
    """Takes the latitude and longitude of a location and returns weather data at that location. Defaults to imperial units, standard and metric are alternative options"""
    # Call the API
    try:
        api_key = os.environ.get("WEATHER_API_KEY") 
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lng}&units={units}&appid={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    
    # Parse out json and return WeatherInfo class object
    try:
        rawdata = response.json()
        weather = WeatherInfo(**rawdata)
        return weather

    except (KeyError, TypeError, ValueError):
        return None
def geocode(zip_code):
    """Takes address information (only zip code for now) and returns a dictionary of latitude and longitude for the location as lat and lng"""
    # Call API
    try:
        api_key = os.environ.get("GEOCODE_API_KEY")
        url=f"https://maps.googleapis.com/maps/api/geocode/json?address={zip_code}&key={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    
    # Parse out json and return latitude and longitude
    try:
        location_data = response.json()
        return location_data["results"][0]["geometry"]["location"]
    except (KeyError, TypeError, ValueError):
        return None
