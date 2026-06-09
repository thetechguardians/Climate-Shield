import os
import sys
import requests

from dotenv import load_dotenv

load_dotenv()

from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory
)

from flask_cors import CORS

# =========================================================
# APP CONFIG
# =========================================================

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "Frontend"
)

CHATBOT_DIR = os.path.join(BASE_DIR, "AI-chatbot")
if CHATBOT_DIR not in sys.path:
    sys.path.insert(0, CHATBOT_DIR)

from chatbot import handle_chatbot_request

# =========================================================
# FRONTEND ROUTES
# =========================================================

@app.route("/")
def home():
    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


@app.route("/Analysis/<path:filename>")
def analysis_files(filename):
    return send_from_directory(
        os.path.join(FRONTEND_DIR, "Analysis"),
        filename
    )


@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(
        FRONTEND_DIR,
        filename
    )

# =========================================================
# WEATHER API
# =========================================================

@app.route("/weather", methods=["POST"])
def get_weather_insights():

    try:

        payload = request.get_json() or {}

        city = payload.get("city", "").strip()
        state = payload.get("state", "").strip()
        country = payload.get("country", "").strip()

        if not city or not state or not country:

            return jsonify({
                "success": False,
                "message": "Please fill all fields."
            }), 400

        api_key = os.environ.get("OPENWEATHER_API_KEY")

        if not api_key:
            print("OPENWEATHER_API_KEY missing")

            return jsonify({
                "success": False,
                "message": "Weather service configuration error."
            }), 500

# ----------------------------------------------------
# STEP 1: Convert city → coordinates
# ----------------------------------------------------

        geo_response = requests.get(
            "https://api.openweathermap.org/geo/1.0/direct",
            params={
                "q": f"{city},{state},{country}",
                "limit": 1,
                "appid": api_key
            },
            timeout=15
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        if not geo_data:
            return jsonify({
                "success": False,
                "message": "Location not found."
            }), 404

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # ----------------------------------------------------
        # STEP 2: Current weather
        # ----------------------------------------------------

        weather_response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": lat,
                "lon": lon,
                "units": "metric",
                "appid": api_key
            },
            timeout=15
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        temp_val = weather_data["main"]["temp"]
        humid_val = weather_data["main"]["humidity"]

        wind_val = round(
            weather_data["wind"]["speed"] * 3.6,
            1
        )

        rain_val = (
            weather_data.get("rain", {}).get("1h")
            or weather_data.get("rain", {}).get("3h")
            or 0
        )

        # ----------------------------------------------------
        # STEP 3: Forecast
        # ----------------------------------------------------

        forecast_response = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "lat": lat,
                "lon": lon,
                "units": "metric",
                "appid": api_key
            },
            timeout=15
        )

        forecast_response.raise_for_status()

        forecast_data = forecast_response.json()

        # ----------------------------------------------------
        # RISK CALCULATIONS
        # ----------------------------------------------------

        flood_risk_metric = round(
            min(
                1.0,
                (
                    rain_val * 0.6 +
                    humid_val * 0.3 +
                    wind_val * 0.1
                ) / 100
            ),
            3
        )

        heat_risk_metric = round(
            min(
                1.0,
                (
                    max(temp_val - 25, 0) * 2 +
                    humid_val * 0.3
                ) / 100
            ),
            3
        )

        wildfire_risk_metric = round(
            min(
                1.0,
                (
                    max(temp_val - 32, 0) * 1.5 +
                    (100 - humid_val) * 0.5 +
                    wind_val * 0.2
                ) / 100
            ),
            3
        )

        cyclone_risk_metric = round(
            min(
                1.0,
                (
                    wind_val * 1.5 +
                    rain_val * 0.5
                ) / 100
            ),
            3
        )

        drought_risk_metric = round(
            min(
                1.0,
                (
                    max(temp_val - 28, 0) +
                    (100 - humid_val)
                ) / 100
            ),
            3
        )

        # ----------------------------------------------------
        # ALERTS
        # ----------------------------------------------------

        calculated_alerts = []

        if flood_risk_metric >= 0.6:
            calculated_alerts.append(
                "⚠ High Flood Risk Detected"
            )

        if heat_risk_metric >= 0.6:
            calculated_alerts.append(
                "🔥 Heatwave Conditions Possible"
            )

        if wildfire_risk_metric >= 0.6:
            calculated_alerts.append(
                "🌲 Elevated Wildfire Risk"
            )

        if cyclone_risk_metric >= 0.6:
            calculated_alerts.append(
                "🌀 Cyclone Risk Detected"
            )

        if drought_risk_metric >= 0.6:
            calculated_alerts.append(
                "☀ Drought Conditions Possible"
            )

        if not calculated_alerts:
            calculated_alerts.append(
                "✅ No major climate threats detected."
            )

        # ----------------------------------------------------
        # FORECAST GENERATION
        # ----------------------------------------------------

        forecast = []

        forecast_items = forecast_data.get("list", [])

        for item in forecast_items[::8][:5]:

            day_temp = item["main"]["temp"]
            day_humidity = item["main"]["humidity"]

            day_rain = (
                item.get("rain", {})
                .get("3h", 0)
            )

            day_wind = round(
                item["wind"]["speed"] * 3.6,
                1
            )

            forecast.append({
                "date": item["dt_txt"],
                "temperature": round(day_temp, 1),
                "humidity": day_humidity,
                "rainfall": round(day_rain, 1),
                "wind_speed": day_wind,
                "risks": {
                    "flood_risk": round(
                        min(
                            1.0,
                            (
                                day_rain * 0.6 +
                                day_humidity * 0.3 +
                                day_wind * 0.1
                            ) / 100
                        ),
                        3
                    ),
                    "heat_risk": round(
                        min(
                            1.0,
                            (
                                max(day_temp - 25, 0) * 2 +
                                day_humidity * 0.3
                            ) / 100
                        ),
                        3
                    ),
                    "wildfire_risk": round(
                        min(
                            1.0,
                            (
                                max(day_temp - 32, 0) * 1.5 +
                                (100 - day_humidity) * 0.5 +
                                day_wind * 0.2
                            ) / 100
                        ),
                        3
                    ),
                    "cyclone_risk": round(
                        min(
                            1.0,
                            (
                                day_wind * 1.5 +
                                day_rain * 0.5
                            ) / 100
                        ),
                        3
                    ),
                    "drought_risk": round(
                        min(
                            1.0,
                            (
                                max(day_temp - 28, 0) +
                                (100 - day_humidity)
                            ) / 100
                        ),
                        3
                    )
                }
            })

        return jsonify({

            "success": True,

            "location": {
                "city": geo_data[0].get("name", city),
                "state": geo_data[0].get("state", state),
                "country": geo_data[0].get("country", country),
                "latitude": lat,
                "longitude": lon
            },

            "weather": {
                "temperature": temp_val,
                "humidity": humid_val,
                "rainfall": rain_val,
                "wind_speed": wind_val
            },

            "risks": {
    "flood_risk": round(flood_risk_metric, 3),
    "flood_risk_confidence": round(flood_risk_metric * 100, 1),
    "flood_risk_level": "HIGH" if flood_risk_metric >= 0.6 else "MEDIUM" if flood_risk_metric >= 0.3 else "LOW",
    "heat_risk": round(heat_risk_metric, 3),
    "heat_risk_confidence": round(heat_risk_metric * 100, 1),
    "heat_risk_level": "HIGH" if heat_risk_metric >= 0.6 else "MEDIUM" if heat_risk_metric >= 0.3 else "LOW",
    "wildfire_risk": round(wildfire_risk_metric, 3),
    "wildfire_risk_confidence": round(wildfire_risk_metric * 100, 1),
    "wildfire_risk_level": "HIGH" if wildfire_risk_metric >= 0.6 else "MEDIUM" if wildfire_risk_metric >= 0.3 else "LOW",
    "cyclone_risk": round(cyclone_risk_metric, 3),
    "cyclone_risk_confidence": round(cyclone_risk_metric * 100, 1),
    "cyclone_risk_level": "HIGH" if cyclone_risk_metric >= 0.6 else "MEDIUM" if cyclone_risk_metric >= 0.3 else "LOW",
    "drought_risk": round(drought_risk_metric, 3),
    "drought_risk_confidence": round(drought_risk_metric * 100, 1),
"drought_risk_level": "HIGH" if drought_risk_metric >= 0.6 else "MEDIUM" if drought_risk_metric >= 0.3 else "LOW",
            },

            "forecast": forecast,

            "alerts": calculated_alerts,
        })

    except Exception as general_err:
        print("Weather Route Error:")
        print(str(general_err))
        return jsonify({"success": False, "message": "Internal server error."}), 500

@app.route("/reverse-geocode", methods=["POST"])
def reverse_geocode():

    try:

        data = request.get_json()

        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if latitude is None or longitude is None:

            return jsonify({
                "success": False,
                "message":
                "Latitude and longitude are required."
            })

        api_key = os.environ.get(
            "OPENWEATHER_API_KEY"
        )

        response = requests.get(
            "https://api.openweathermap.org/geo/1.0/reverse",
            params={
                "lat": latitude,
                "lon": longitude,
                "limit": 1,
                "appid": api_key
            },
            timeout=20
        )

        if response.status_code != 200:

            return jsonify({
                "success": False,
                "message":
                "Reverse geocoding failed."
            })

        result = response.json()

        if not result:

            return jsonify({
                "success": False,
                "message":
                "Location not found."
            })

        location = result[0]

        return jsonify({

            "success": True,

            "city":
            location.get("name", ""),

            "state":
            location.get("state", ""),

            "country":
            location.get("country", "")

        })

    except Exception:

        return jsonify({
            "success": False,
            "message":
            "Reverse geocoding failed."
        })


# =========================================================
# CHATBOT API
# =========================================================

@app.route("/chatbot", methods=["POST"])
def chatbot():

    try:
        data = request.get_json(silent=True) or {}
        payload, status = handle_chatbot_request(data)
        return jsonify(payload), status

    except Exception:

        return jsonify({
            "success": False,
            "message":
            "Chatbot unavailable."
        })

# =========================================================
# LOCAL RUN
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
