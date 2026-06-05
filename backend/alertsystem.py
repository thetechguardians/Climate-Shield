import os
import requests

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
# THRESHOLDS
# =========================================================

FLOOD_RISK_THRESHOLD     = 0.65
HEAT_RISK_THRESHOLD      = 0.75
WILDFIRE_RISK_THRESHOLD  = 0.65
CYCLONE_RISK_THRESHOLD   = 0.60
DROUGHT_RISK_THRESHOLD   = 0.70

# =========================================================
# GET LOCATION COORDINATES (Nominatim / OpenStreetMap)
# =========================================================

def get_coordinates(city, state, country):

    url = "https://nominatim.openstreetmap.org/search"

    headers = {
        "User-Agent": "ClimateWeatherApp/1.0"
    }

    # -------------------------------------------------
    # ATTEMPT 1: city + state + country (most specific)
    # -------------------------------------------------

    params = {
        "city":    city,
        "state":   state,
        "country": country,
        "format":  "json",
        "limit":   1
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=20
        )

        print("Geocoding Status (attempt 1):", response.status_code)

        data = response.json()

        print("Geocoding Data (attempt 1):", data)

        # -------------------------------------------------
        # ATTEMPT 2: if attempt 1 failed, try city + country
        # -------------------------------------------------

        if not data:

            print("Attempt 1 failed. Retrying with city + country only...")

            params = {
                "city":    city,
                "country": country,
                "format":  "json",
                "limit":   1
            }

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=20
            )

            print("Geocoding Status (attempt 2):", response.status_code)

            data = response.json()

            print("Geocoding Data (attempt 2):", data)

        # -------------------------------------------------
        # ATTEMPT 3: if still failed, try free-text query
        # -------------------------------------------------

        if not data:

            print("Attempt 2 failed. Retrying with free-text query...")

            params = {
                "q":      f"{city}, {country}",
                "format": "json",
                "limit":  1
            }

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=20
            )

            print("Geocoding Status (attempt 3):", response.status_code)

            data = response.json()

            print("Geocoding Data (attempt 3):", data)

        # -------------------------------------------------
        # FINAL CHECK
        # -------------------------------------------------

        if not data:
            return None

        location = data[0]

        return {
            "latitude":  float(location["lat"]),
            "longitude": float(location["lon"]),
            "city":      location.get("display_name", city).split(",")[0].strip(),
            "state":     state,
            "country":   country
        }

    except Exception as e:
        print("Geocoding Error:")
        print(str(e))
        return None

# =========================================================
# GIS ALERT DATA (Issue #83: Exception Handling)
# =========================================================

def fetch_gis_alert_data():
    """
    Fetches external GIS climate data streams.
    Implements try-except blocks to prevent backend crashes.
    """
    GIS_API_URL = "https://external-gis-source.com"

    try:
        response = requests.get(GIS_API_URL, timeout=5)
        response.raise_for_status()
        return response.json(), 200

    except requests.exceptions.Timeout:
        return {"error": "External GIS service timed out. Please try again."}, 504

    except (requests.exceptions.RequestException, ValueError):
        return {"error": "External GIS service is unavailable or returned an invalid response."}, 503

# =========================================================
# WEATHER API
# =========================================================

@app.route("/weather", methods=["POST"])
def get_weather_insights():

    try:

        payload = request.get_json() or {}

        city    = payload.get("city",    "").strip()
        state   = payload.get("state",   "").strip()
        country = payload.get("country", "").strip()

        if not city or not state or not country:
            return jsonify({
                "success": False,
                "message": "Please fill all fields."
            }), 400

        # ----------------------------------------------------
        # STEP 1: Convert city → coordinates via Nominatim
        # ----------------------------------------------------

        coords = get_coordinates(city, state, country)

        if not coords:
            return jsonify({
                "success": False,
                "message": "Location not found."
            }), 404

        lat = coords["latitude"]
        lon = coords["longitude"]

        # ----------------------------------------------------
        # STEP 2: Current weather (OpenWeatherMap)
        # ----------------------------------------------------

        api_key = os.environ.get("OPENWEATHER_API_KEY")

        if not api_key:
            print("OPENWEATHER_API_KEY missing")
            return jsonify({
                "success": False,
                "message": "Weather service configuration error."
            }), 500

        weather_response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat":   lat,
                "lon":   lon,
                "units": "metric",
                "appid": api_key
            },
            timeout=15
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        temp_val  = weather_data["main"]["temp"]
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
                "lat":   lat,
                "lon":   lon,
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
            min(1.0, (rain_val * 0.6 + humid_val * 0.3 + wind_val * 0.1) / 100),
            3
        )

        heat_risk_metric = round(
            min(1.0, (max(temp_val - 25, 0) * 2 + humid_val * 0.3) / 100),
            3
        )

        wildfire_risk_metric = round(
            min(1.0, (max(temp_val - 32, 0) * 1.5 + (100 - humid_val) * 0.5 + wind_val * 0.2) / 100),
            3
        )

        cyclone_risk_metric = round(
            min(1.0, (wind_val * 1.5 + rain_val * 0.5) / 100),
            3
        )

        drought_risk_metric = round(
            min(1.0, (max(temp_val - 28, 0) + (100 - humid_val)) / 100),
            3
        )

        # ----------------------------------------------------
        # ALERTS
        # ----------------------------------------------------

        calculated_alerts = []

        if flood_risk_metric >= FLOOD_RISK_THRESHOLD:
            calculated_alerts.append("⚠ High Flood Risk Detected")

        if heat_risk_metric >= HEAT_RISK_THRESHOLD:
            calculated_alerts.append("🔥 Heatwave Conditions Possible")

        if wildfire_risk_metric >= WILDFIRE_RISK_THRESHOLD:
            calculated_alerts.append("🌲 Elevated Wildfire Risk")

        if cyclone_risk_metric >= CYCLONE_RISK_THRESHOLD:
            calculated_alerts.append("🌀 Cyclone Risk Detected")

        if drought_risk_metric >= DROUGHT_RISK_THRESHOLD:
            calculated_alerts.append("☀ Drought Conditions Possible")

        if not calculated_alerts:
            calculated_alerts.append("✅ No major climate threats detected.")

        # ----------------------------------------------------
        # FORECAST GENERATION
        # ----------------------------------------------------

        forecast = []

        forecast_items = forecast_data.get("list", [])

        for item in forecast_items[::8][:5]:

            day_temp     = item["main"]["temp"]
            day_humidity = item["main"]["humidity"]
            day_rain     = item.get("rain", {}).get("3h", 0)
            day_wind     = round(item["wind"]["speed"] * 3.6, 1)

            forecast.append({
                "date":        item["dt_txt"],
                "temperature": round(day_temp, 1),
                "humidity":    day_humidity,
                "rainfall":    round(day_rain, 1),
                "wind_speed":  day_wind,
                "risks": {
                    "flood_risk": round(
                        min(1.0, (day_rain * 0.6 + day_humidity * 0.3 + day_wind * 0.1) / 100), 3
                    ),
                    "heat_risk": round(
                        min(1.0, (max(day_temp - 25, 0) * 2 + day_humidity * 0.3) / 100), 3
                    ),
                    "wildfire_risk": round(
                        min(1.0, (max(day_temp - 32, 0) * 1.5 + (100 - day_humidity) * 0.5 + day_wind * 0.2) / 100), 3
                    ),
                    "cyclone_risk": round(
                        min(1.0, (day_wind * 1.5 + day_rain * 0.5) / 100), 3
                    ),
                    "drought_risk": round(
                        min(1.0, (max(day_temp - 28, 0) + (100 - day_humidity)) / 100), 3
                    )
                }
            })

        return jsonify({

            "success": True,

            "location": {
                "city":      coords["city"],
                "state":     coords["state"],
                "country":   coords["country"],
                "latitude":  lat,
                "longitude": lon
            },

            "weather": {
                "temperature": temp_val,
                "humidity":    humid_val,
                "rainfall":    rain_val,
                "wind_speed":  wind_val
            },

            "risks": {
                "flood_risk":    round(flood_risk_metric,    3),
                "heat_risk":     round(heat_risk_metric,     3),
                "wildfire_risk": round(wildfire_risk_metric, 3),
                "cyclone_risk":  round(cyclone_risk_metric,  3),
                "drought_risk":  round(drought_risk_metric,  3)
            },

            "forecast": forecast,

            "alerts": calculated_alerts,

            "demo_mode": False

        }), 200

    except Exception as e:

        print("Weather API Error:", e)

        return jsonify({
            "success": False,
            "message": "Weather service unavailable."
        }), 500

# =========================================================
# REVERSE GEOCODE
# =========================================================

@app.route("/reverse-geocode", methods=["POST"])
def reverse_geocode():

    try:

        data = request.get_json()

        latitude  = data.get("latitude")
        longitude = data.get("longitude")

        if latitude is None or longitude is None:
            return jsonify({
                "success": False,
                "message": "Latitude and longitude are required."
            })

        api_key = os.environ.get("OPENWEATHER_API_KEY")

        response = requests.get(
            "https://api.openweathermap.org/geo/1.0/reverse",
            params={
                "lat":   latitude,
                "lon":   longitude,
                "limit": 1,
                "appid": api_key
            },
            timeout=20
        )

        if response.status_code != 200:
            return jsonify({
                "success": False,
                "message": "Reverse geocoding failed."
            })

        result = response.json()

        if not result:
            return jsonify({
                "success": False,
                "message": "Location not found."
            })

        location = result[0]

        return jsonify({
            "success": True,
            "city":    location.get("name",    ""),
            "state":   location.get("state",   ""),
            "country": location.get("country", "")
        })

    except Exception:
        return jsonify({
            "success": False,
            "message": "Reverse geocoding failed."
        })

# =========================================================
# CHATBOT API
# =========================================================

@app.route("/chatbot", methods=["POST"])
def chatbot():

    try:

        data    = request.get_json()
        message = data.get("message", "").lower()

        responses = {
            "flood":     "Floods are caused by heavy rainfall and overflowing rivers. Avoid low-lying areas.",
            "heatwave":  "Heatwaves can cause dehydration and heat stroke. Stay hydrated and avoid direct sunlight.",
            "cyclone":   "Cyclones bring strong winds and heavy rain. Follow evacuation advisories.",
            "earthquake":"During earthquakes, stay away from windows and take cover under sturdy furniture.",
            "climate":   "Climate change increases the frequency of extreme weather events.",
            "rain":      "Heavy rainfall may increase flood risks in vulnerable regions."
        }

        for key in responses:
            if key in message:
                return jsonify({
                    "success":  True,
                    "response": responses[key]
                })

        return jsonify({
            "success":  True,
            "response": "ClimateBot is ready to help with floods, cyclones, heatwaves, and climate safety."
        })

    except Exception:
        return jsonify({
            "success": False,
            "message": "Chatbot unavailable."
        })

# =========================================================
# LOCAL RUN
# =========================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )