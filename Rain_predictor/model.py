import requests
import pandas as pd
from geopy.geocoders import Nominatim
import joblib
model=joblib.load("xgb_model_weather.joblib")
def get_coordinates(location_dict):#obtain the coordinates using the location input by the user
  city=location_dict.get("city","").strip()
  state=location_dict.get("state","").strip()
  country=location_dict.get("country","").strip()
  geolocator = Nominatim(user_agent="weather_predictor_2026")
  location_string=f"{city}, {state}, {country}".strip(",")

  try:
    location=geolocator.geocode(location_string)
    if not location:
      location_string=f"{state},{country}".strip(",")
      location=geolocator.geocode(location_string)
    if not location:
      location_string=country
      location=geolocator.geocode(location_string)
    return location.latitude,location.longitude
  except Exception as e:
    return None,None

def extract_features(location_dict):# extract the features from open weather
  lat,lon=get_coordinates(location_dict)
  if not lat or not lon:
    return "Coordinates not fetched."
  API_KEY=""
  url=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
  response=requests.get(url).json()
  if response.get('cod') != 200:
    return "Failed api call"
  openweather_temp=response['main']['temp']
  openweather_humidity = response['main']['humidity']
  openweather_wind_speed = response['wind']['speed']*3.6
  openweather_wind_dir = response['wind']['deg']
  openweather_gusts = response['wind'].get('gust', openweather_wind_speed * 1.2)*3.6
  lat_rad = np.radians(lat)
  lon_rad = np.radians(lon)
  coord_x= np.cos(lat_rad) * np.cos(lon_rad)
  coord_y= np.cos(lat_rad) * np.sin(lon_rad)
  coord_z= np.sin(lat_rad)

  live_features = pd.DataFrame({
"latitude":lat,
"longitude":lon,
"wind_direction_10m_dominant": openweather_wind_dir,
"wind_speed_10m_mean": openweather_wind_speed,
"wind_gusts_10m_mean": openweather_gusts,
"temperature_2m_mean": openweather_temp,
"relative_humidity_2m_mean": openweather_humidity,
"coord_x":coord_x,
"coord_y":coord_y,
"coord_z":coord_z}, index=[0])
  result=model.predict(live_features)
  return result
  
def get_rain_criteria(location_dict):
  '''Takes the resulr from the extract_feature function and predict the likeability of rain.'''
  result=extract_features(location_dict)
 try:
   if rain_mm <= 2.4:
        return "No Rain / Light Drizzle ☀️"
    elif 2.4 < rain_mm <= 15.5:
        return "Light Rain 🌧️"
    elif 15.5 < rain_mm <= 64.4:
        return "Moderate Rain ⛈️"
    elif 64.4 < rain_mm <= 115.5:
        return "Heavy Rain Alert 🚨"
    elif 115.5 < rain_mm <= 204.4:
        return "Very Heavy Rain Warning 🌊"
    else:
        return "Extremely Heavy Rain / Flood Risk ⚠️"
  except Exception as e:
    return "Rain status could not be found."
  
  

    
