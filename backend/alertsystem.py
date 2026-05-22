import random

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

app = Flask(
    __name__,
    static_folder="../Frontend",
    static_url_path=""
)

@app.route("/")
def home():

    return send_from_directory(
        app.static_folder,
        "Index.html"
    )

CORS(app)

FLOOD_RISK_THRESHOLD = 0.65
HEAT_RISK_THRESHOLD = 0.75


# ==========================================
# GET LOCATION COORDINATES
# ==========================================

def get_coordinates(city, state, country):

    url = (
        f"https://geocoding-api.open-meteo.com/v1/search?"
        f"name={city}&count=10"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    if "results" not in data:
        return None

    results = data["results"]

    state = state.lower().strip()
    country = country.lower().strip()

    for result in results:

        result_state = result.get("admin1", "").lower()
        result_country = result.get("country", "").lower()

        if state in result_state and country in result_country:

            return {
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "city": result["name"],
                "state": result.get("admin1", state.title()),
                "country": result["country"]
            }

    return None


# ==========================================
# FETCH WEATHER
# ==========================================

def fetch_weather(latitude, longitude):

    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}"
        f"&longitude={longitude}"
        "&current="
        "temperature_2m,"
        "relative_humidity_2m,"
        "precipitation,"
        "wind_speed_10m"
    )

    try:

        response = requests.get(

            url,

            headers={
                "User-Agent":
                "ClimateShield/1.0"
            },

            timeout=15

        )

        if response.status_code != 200:

            print("Weather API Error:",
                  response.text)

            return None

        data = response.json()

        if "current" not in data:

            print("No current weather data")

            return None

        current = data["current"]

        return {

            "temperature":
            current.get("temperature_2m", 0),

            "humidity":
            current.get(
                "relative_humidity_2m",
                0
            ),

            "rainfall":
            current.get("precipitation", 0),

            "wind_speed":
            current.get("wind_speed_10m", 0)

        }

    except Exception as e:

        print("Weather Fetch Error:", e)

        return None

# ==========================================
# FLOOD RISK
# ==========================================

def calculate_flood_risk(weather):

    rainfall = weather["rainfall"]
    humidity = weather["humidity"]
    wind_speed = weather["wind_speed"]

    risk_score = (

        0.5 * min(rainfall / 50, 1)
        +
        0.3 * (humidity / 100)
        +
        0.2 * min(wind_speed / 40, 1)

    )

    return round(risk_score, 2)


# ==========================================
# HEAT RISK
# ==========================================

def calculate_heat_risk(weather):

    temperature = weather["temperature"]
    humidity = weather["humidity"]

    heat_index = temperature + (0.33 * humidity) - 4

    risk_score = min(heat_index / 50, 1)

    return round(risk_score, 2)


# ==========================================
# API ROUTE
# ==========================================

@app.route("/weather", methods=["POST"])
def weather_analysis():

    data = request.get_json()

    city = data["city"]
    state = data["state"]
    country = data["country"]

    location = get_coordinates(
        city,
        state,
        country
    )

    if location is None:

        return jsonify({
            "success": False,
            "message": "Location not found."
        })

    weather = fetch_weather(
        location["latitude"],
        location["longitude"]
    )

    if weather is None:

        return jsonify({
            "success": False,
            "message": "Weather unavailable."
        })

    flood_risk = calculate_flood_risk(weather)
    heat_risk = calculate_heat_risk(weather)

    alerts = []

    if flood_risk >= FLOOD_RISK_THRESHOLD:

        alerts.append(
            "⚠ Flood Risk Detected"
        )

    if heat_risk >= HEAT_RISK_THRESHOLD:

        alerts.append(
            "☀ Heatwave Risk Detected"
        )

    if len(alerts) == 0:

        alerts.append(
            "✅ No major climate risks detected"
        )

    return jsonify({

        "success": True,

        "location": {

            "city": location["city"],
            "state": location["state"],
            "country": location["country"]

        },

        "weather": weather,

        "risks": {

            "flood_risk": flood_risk,
            "heat_risk": heat_risk

        },

        "alerts": alerts

    })

@app.route("/chatbot", methods=["POST"])
def chatbot():

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
                "response": responses[key]

            })

    return jsonify({

        "success": True,

        "response":
        "ClimateBot is ready to help with floods, heatwaves, cyclones, rainfall, and climate safety."

    })

# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":

    import os

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )