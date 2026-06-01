import os
import requests

from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

from flask_cors import CORS
from dotenv import load_dotenv

# =========================================================
# LOAD ENV VARIABLES
# =========================================================

load_dotenv()

# =========================================================
# FLASK APP
# =========================================================

app = Flask(
    __name__,
    static_folder="../Frontend",
    static_url_path=""
)

CORS(app)

# =========================================================
# FRONTEND ROUTES
# =========================================================

@app.route("/")
def home():

    return send_from_directory(
        app.static_folder,
        "index.html"
    )


@app.route("/Analysis/analysis.html")
def analysis_page():

    return send_from_directory(
        "../Frontend/Analysis",
        "analysis.html"
    )


@app.route("/Analysis/<path:filename>")
def analysis_static(filename):

    return send_from_directory(
        "../Frontend/Analysis",
        filename
    )


@app.route("/<path:filename>")
def frontend_static(filename):

    return send_from_directory(
        app.static_folder,
        filename
    )

# =========================================================
# THRESHOLDS
# =========================================================

FLOOD_RISK_THRESHOLD = 0.65
HEAT_RISK_THRESHOLD = 0.75
WILDFIRE_RISK_THRESHOLD = 0.65
CYCLONE_RISK_THRESHOLD = 0.60
DROUGHT_RISK_THRESHOLD = 0.70

# =========================================================
# GET LOCATION COORDINATES (WITH MOCK FALLBACK)
# =========================================================

def get_mock_coordinates(city, state, country):
    import hashlib
    h = int(hashlib.md5(city.lower().encode('utf-8')).hexdigest(), 16)
    # Generate coordinates centered dynamically around the hashed location
    lat = round(10.0 + (h % 35) + ((h % 100) / 100.0), 4)
    lon = round(60.0 + ((h >> 8) % 35) + (((h >> 8) % 100) / 100.0), 4)
    return {
        "latitude": lat,
        "longitude": lon,
        "city": city.title(),
        "state": state.title(),
        "country": country.upper(),
        "mock": True
    }

def get_coordinates(city, state, country):
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("Using Mock coordinates (No API Key configured)")
        return get_mock_coordinates(city, state, country)

    url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": f"{city},{state},{country}",
        "limit": 5,
        "appid": api_key
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )
        print("Geocoding Status:", response.status_code)
        if response.status_code == 401:
            print("Geocoding 401 (Invalid Key). Falling back to Mock coordinates.")
            return get_mock_coordinates(city, state, country)
        if response.status_code != 200:
            print(response.text)
            return get_mock_coordinates(city, state, country)

        data = response.json()
        print("Geocoding Data:", data)
        if not data:
            return get_mock_coordinates(city, state, country)

        location = data[0]
        return {
            "latitude": location["lat"],
            "longitude": location["lon"],
            "city": location.get("name", city),
            "state": location.get("state", state),
            "country": location.get("country", country),
            "mock": False
        }
    except Exception as e:
        print("Geocoding Error, using Mock:")
        print(str(e))
        return get_mock_coordinates(city, state, country)

# =========================================================
# FETCH WEATHER (WITH MOCK FALLBACK)
# =========================================================

def get_mock_weather(latitude, longitude):
    import hashlib
    h = int(hashlib.md5(f"{latitude},{longitude}".encode('utf-8')).hexdigest(), 16)
    # Generate realistic pseudo-random values based on coords
    temp = round(15.0 + (h % 22) + ((h % 10) / 10.0), 1)  # 15 to 37 °C
    humidity = 40 + (h % 51)  # 40% to 90%
    wind_speed = round(3.0 + ((h >> 4) % 32) + (((h >> 4) % 10) / 10.0), 1)  # 3 to 35 km/h
    rainfall = round(((h >> 8) % 15) + (((h >> 8) % 10) / 10.0), 1) if humidity > 75 else 0.0
    return {
        "temperature": temp,
        "humidity": humidity,
        "rainfall": rainfall,
        "wind_speed": wind_speed
    }

def fetch_weather(latitude, longitude, is_mock=False):
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if is_mock or not api_key or api_key == "your_api_key_here":
        return get_mock_weather(latitude, longitude)

    url = (
        "https://api.openweathermap.org/data/2.5/weather?"
        f"lat={latitude}"
        f"&lon={longitude}"
        f"&appid={api_key}"
        "&units=metric"
    )

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )
        print("Weather Status:", response.status_code)
        if response.status_code == 401:
            print("Weather fetch 401. Falling back to Mock weather.")
            return get_mock_weather(latitude, longitude)
        if response.status_code != 200:
            print(response.text)
            return get_mock_weather(latitude, longitude)

        data = response.json()
        print("Weather Data:", data)
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "rainfall": data.get("rain", {}).get("1h", 0.0),
            "wind_speed": data["wind"]["speed"]
        }
    except Exception as e:
        print("Weather Fetch Error, using Mock:")
        print(str(e))
        return get_mock_weather(latitude, longitude)

# =========================================================
# FETCH FORECAST (WITH MOCK FALLBACK)
# =========================================================

def get_mock_forecast(latitude, longitude):
    import datetime
    weather = get_mock_weather(latitude, longitude)
    forecast_list = []
    for i in range(1, 6):
        date_str = (datetime.date.today() + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        # Introduce mock variations for each day
        day_temp = round(weather["temperature"] + (i * 1.5 - 4) * (-1 if i % 2 == 0 else 1), 1)
        day_humidity = min(max(weather["humidity"] + (i * 4 - 10), 30), 100)
        day_wind = max(round(weather["wind_speed"] + (i * 1.2 - 3), 1), 1.0)
        day_rain = round(max(weather["rainfall"] + (i * 2.5 - 5) if day_humidity > 70 else 0.0, 0.0), 1)
        
        forecast_weather = {
            "temperature": day_temp,
            "humidity": day_humidity,
            "rainfall": day_rain,
            "wind_speed": day_wind
        }
        
        forecast_list.append({
            "date": date_str,
            "temperature": day_temp,
            "humidity": day_humidity,
            "rainfall": day_rain,
            "wind_speed": day_wind,
            "risks": {
                "flood_risk": calculate_flood_risk(forecast_weather),
                "heat_risk": calculate_heat_risk(forecast_weather),
                "wildfire_risk": calculate_wildfire_risk(forecast_weather),
                "cyclone_risk": calculate_cyclone_risk(forecast_weather),
                "drought_risk": calculate_drought_risk(forecast_weather)
            }
        })
    return forecast_list

def fetch_forecast(latitude, longitude, is_mock=False):
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if is_mock or not api_key or api_key == "your_api_key_here":
        return get_mock_forecast(latitude, longitude)

    url = (
        "https://api.openweathermap.org/data/2.5/forecast?"
        f"lat={latitude}"
        f"&lon={longitude}"
        f"&appid={api_key}"
        "&units=metric"
    )

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )
        print("Forecast Status:", response.status_code)
        if response.status_code == 401:
            print("Forecast fetch 401. Falling back to Mock forecast.")
            return get_mock_forecast(latitude, longitude)
        if response.status_code != 200:
            print(response.text)
            return get_mock_forecast(latitude, longitude)

        data = response.json()
        forecast_list = []
        items = data.get("list", [])
        # OpenWeather returns forecast intervals every 3 hours. Filter daily mid-day (12:00:00) readings
        daily_items = [item for item in items if "12:00:00" in item.get("dt_txt", "")]
        if not daily_items and items:
            daily_items = items[::8][:5]

        for item in daily_items:
            forecast_weather = {
                "temperature": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "rainfall": item.get("rain", {}).get("3h", 0.0) / 3.0,  # convert 3-hourly accumulation to estimate hourly
                "wind_speed": item["wind"]["speed"]
            }
            forecast_list.append({
                "date": item.get("dt_txt", "").split(" ")[0],
                "temperature": round(forecast_weather["temperature"], 1),
                "humidity": forecast_weather["humidity"],
                "rainfall": round(forecast_weather["rainfall"], 2),
                "wind_speed": round(forecast_weather["wind_speed"], 1),
                "risks": {
                    "flood_risk": calculate_flood_risk(forecast_weather),
                    "heat_risk": calculate_heat_risk(forecast_weather),
                    "wildfire_risk": calculate_wildfire_risk(forecast_weather),
                    "cyclone_risk": calculate_cyclone_risk(forecast_weather),
                    "drought_risk": calculate_drought_risk(forecast_weather)
                }
            })
        return forecast_list
    except Exception as e:
        print("Forecast Fetch Error, using Mock:")
        print(str(e))
        return get_mock_forecast(latitude, longitude)

# =========================================================
# FLOOD RISK
# =========================================================

def calculate_flood_risk(weather):
    rainfall = weather["rainfall"]
    humidity = weather["humidity"]
    wind_speed = weather["wind_speed"]

    risk_score = (
        0.5 * min(rainfall / 50, 1)
        + 0.3 * (humidity / 100)
        + 0.2 * min(wind_speed / 40, 1)
    )
    return round(risk_score, 2)

# =========================================================
# HEAT RISK
# =========================================================

def calculate_heat_risk(weather):
    temperature = weather["temperature"]
    humidity = weather["humidity"]

    heat_index = temperature + (0.33 * humidity) - 4
    risk_score = min(heat_index / 50, 1)
    return round(risk_score, 2)

# =========================================================
# WILDFIRE RISK
# =========================================================

def calculate_wildfire_risk(weather):
    temperature = weather["temperature"]
    humidity = weather["humidity"]
    wind_speed = weather["wind_speed"]

    # Higher temperature, lower humidity, and higher wind speeds increase wildfire risk
    t_factor = min(max(temperature - 15, 0) / 25, 1)  # 0 at 15C, 1 at 40C
    h_factor = min(max(100 - humidity, 0) / 80, 1)    # 1 at 20% humidity, 0 at 100%
    w_factor = min(wind_speed / 40, 1)                # 1 at 40+ km/h

    risk_score = 0.4 * t_factor + 0.3 * h_factor + 0.3 * w_factor
    return round(min(max(risk_score, 0), 1), 2)

# =========================================================
# CYCLONE RISK
# =========================================================

def calculate_cyclone_risk(weather):
    wind_speed = weather["wind_speed"]
    rainfall = weather["rainfall"]

    # Extremely high wind speeds combined with rain indicate cyclone threat
    w_factor = min(wind_speed / 60, 1)
    r_factor = min(rainfall / 30, 1)

    risk_score = 0.6 * w_factor + 0.4 * r_factor
    return round(min(max(risk_score, 0), 1), 2)

# =========================================================
# DROUGHT RISK
# =========================================================

def calculate_drought_risk(weather):
    temperature = weather["temperature"]
    humidity = weather["humidity"]
    rainfall = weather["rainfall"]

    # High temperature, low humidity, and lack of rain lead to drought
    t_factor = min(max(temperature - 20, 0) / 20, 1)  # 0 at 20C, 1 at 40C
    h_factor = min(max(80 - humidity, 0) / 60, 1)     # 1 at 20% humidity, 0 at 80%+
    r_factor = max(1 - (rainfall / 10), 0)            # 1 at 0 rain, 0 at 10mm+ rain

    risk_score = 0.4 * t_factor + 0.4 * h_factor + 0.2 * r_factor
    return round(min(max(risk_score, 0), 1), 2)

# =========================================================
# WEATHER API
# =========================================================

@app.route(
    "/weather",
    methods=["POST"]
)
def weather_analysis():
    try:
        print("WEATHER ROUTE HIT")
        data = request.get_json()

        city = data.get("city", "")
        state = data.get("state", "")
        country = data.get("country", "")

        if not city or not state or not country:
            return jsonify({
                "success": False,
                "message": "Please provide city, state, and country."
            })

        # =====================================
        # LOCATION
        # =====================================
        location = get_coordinates(city, state, country)
        if location is None:
            return jsonify({
                "success": False,
                "message": "Location not found."
            })

        is_mock = location.get("mock", False)

        # =====================================
        # WEATHER
        # =====================================
        weather = fetch_weather(location["latitude"], location["longitude"], is_mock)
        if weather is None:
            return jsonify({
                "success": False,
                "message": "Weather unavailable."
            })

        # =====================================
        # FORECAST
        # =====================================
        forecast = fetch_forecast(location["latitude"], location["longitude"], is_mock)

        # =====================================
        # RISKS
        # =====================================
        flood_risk = calculate_flood_risk(weather)
        heat_risk = calculate_heat_risk(weather)
        wildfire_risk = calculate_wildfire_risk(weather)
        cyclone_risk = calculate_cyclone_risk(weather)
        drought_risk = calculate_drought_risk(weather)

        alerts = []
        if flood_risk >= FLOOD_RISK_THRESHOLD:
            alerts.append("⚠ Flood Risk Detected")
        if heat_risk >= HEAT_RISK_THRESHOLD:
            alerts.append("☀ Heatwave Risk Detected")
        if wildfire_risk >= WILDFIRE_RISK_THRESHOLD:
            alerts.append("🔥 Wildfire Risk Detected")
        if cyclone_risk >= CYCLONE_RISK_THRESHOLD:
            alerts.append("🌀 Cyclone Risk Detected")
        if drought_risk >= DROUGHT_RISK_THRESHOLD:
            alerts.append("🌾 Drought Risk Detected")

        if len(alerts) == 0:
            alerts.append("✅ No major climate risks detected")

        # =====================================
        # RESPONSE
        # =====================================
        return jsonify({
            "success": True,
            "demo_mode": is_mock,
            "location": {
                "city": location["city"],
                "state": location["state"],
                "country": location["country"],
                "latitude": location["latitude"],
                "longitude": location["longitude"]
            },
            "weather": {
                "temperature": weather["temperature"],
                "humidity": weather["humidity"],
                "rainfall": weather["rainfall"],
                "wind_speed": weather["wind_speed"]
            },
            "risks": {
                "flood_risk": flood_risk,
                "heat_risk": heat_risk,
                "wildfire_risk": wildfire_risk,
                "cyclone_risk": cyclone_risk,
                "drought_risk": drought_risk
            },
            "forecast": forecast,
            "alerts": alerts
        })

    except Exception as e:
        print("Weather Route Error:")
        print(str(e))
        return jsonify({
            "success": False,
            "message": "Internal server error."
        })

# =========================================================
# CHATBOT API
# =========================================================

@app.route(
    "/chatbot",
    methods=["POST"]
)

def chatbot():

    try:

        data = request.get_json()

        message = data.get(
            "message",
            ""
        ).lower()

        responses = {

            "flood":
            "Floods are caused by heavy rainfall and overflowing rivers. Avoid low-lying areas.",

            "heatwave":
            "Heatwaves can cause dehydration and heat stroke. Stay hydrated and avoid direct sunlight.",

            "cyclone":
            "Cyclones bring strong winds and heavy rain. Follow evacuation advisories.",

            "earthquake":
            "During earthquakes, stay away from windows and take cover under sturdy furniture.",

            "climate":
            "Climate change increases the frequency of extreme weather events.",

            "rain":
            "Heavy rainfall may increase flood risks in vulnerable regions."

        }

        for key in responses:

            if key in message:

                return jsonify({

                    "success": True,

                    "response":
                    responses[key]

                })

        return jsonify({

            "success": True,

            "response":
            "ClimateBot is ready to help with floods, cyclones, heatwaves, and climate safety."

        })

    except Exception as e:

        print("Chatbot Error:")
        print(str(e))

        return jsonify({

            "success": False,

            "message":
            "Chatbot unavailable."

        })

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(

        host="0.0.0.0",

        port=port,

        debug=True

    )