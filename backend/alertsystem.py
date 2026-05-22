import os
import requests

from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

from flask_cors import CORS

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
        "Index.html"
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
# RISK THRESHOLDS
# =========================================================

FLOOD_RISK_THRESHOLD = 0.65
HEAT_RISK_THRESHOLD = 0.75

# =========================================================
# GET COORDINATES
# =========================================================

def get_coordinates(city, state, country):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {

        "name": city,
        "count": 10,
        "language": "en",
        "format": "json"

    }

    try:

        response = requests.get(

            url,

            params=params,

            headers={
                "User-Agent":
                "ClimateShield/1.0"
            },

            timeout=20

        )

        print("Geocoding Status:",
              response.status_code)

        if response.status_code != 200:

            print(response.text)
            return None

        data = response.json()

        results = data.get("results")

        if not results:

            return None

        state = state.lower().strip()
        country = country.lower().strip()

        for result in results:

            result_state = (
                result.get("admin1", "")
                .lower()
                .strip()
            )

            result_country = (
                result.get("country", "")
                .lower()
                .strip()
            )

            if country not in result_country:
                continue

            return {

                "latitude":
                result["latitude"],

                "longitude":
                result["longitude"],

                "city":
                result["name"],

                "state":
                result.get("admin1", state),

                "country":
                result["country"]

            }

        return None

    except Exception as e:

        print("Geocoding Error:")
        print(str(e))

        return None

# =========================================================
# FETCH WEATHER
# =========================================================

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

            timeout=20

        )

        print("Weather Status:",
              response.status_code)

        if response.status_code != 200:

            print(response.text)
            return None

        data = response.json()

        current = data.get("current")

        if not current:

            return None

        return {

            "temperature":
            current.get(
                "temperature_2m",
                0
            ),

            "humidity":
            current.get(
                "relative_humidity_2m",
                0
            ),

            "rainfall":
            current.get(
                "precipitation",
                0
            ),

            "wind_speed":
            current.get(
                "wind_speed_10m",
                0
            )

        }

    except Exception as e:

        print("Weather Fetch Error:")
        print(str(e))

        return None

# =========================================================
# FLOOD RISK
# =========================================================

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

# =========================================================
# HEAT RISK
# =========================================================

def calculate_heat_risk(weather):

    temperature = weather["temperature"]
    humidity = weather["humidity"]

    heat_index = (
        temperature
        +
        (0.33 * humidity)
        -
        4
    )

    risk_score = min(
        heat_index / 50,
        1
    )

    return round(risk_score, 2)

# =========================================================
# WEATHER API
# =========================================================

@app.route("/weather", methods=["POST"])
def weather_analysis():

    try:

        data = request.get_json()

        city = data.get("city", "")
        state = data.get("state", "")
        country = data.get("country", "")

        if not city or not state or not country:

            return jsonify({

                "success": False,

                "message":
                "Please provide city, state, and country."

            })

        # =====================================
        # LOCATION
        # =====================================

        location = get_coordinates(
            city,
            state,
            country
        )

        if location is None:

            return jsonify({

                "success": False,

                "message":
                "Location not found."

            })

        # =====================================
        # WEATHER
        # =====================================

        weather = fetch_weather(

            location["latitude"],
            location["longitude"]

        )

        if weather is None:

            return jsonify({

                "success": False,

                "message":
                "Weather unavailable."

            })

        # =====================================
        # RISKS
        # =====================================

        flood_risk = calculate_flood_risk(
            weather
        )

        heat_risk = calculate_heat_risk(
            weather
        )

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

        # =====================================
        # RESPONSE
        # =====================================

        return jsonify({

            "success": True,

            "location": {

                "city":
                location["city"],

                "state":
                location["state"],

                "country":
                location["country"]

            },

            "weather": {

                "temperature":
                weather["temperature"],

                "humidity":
                weather["humidity"],

                "rainfall":
                weather["rainfall"],

                "wind_speed":
                weather["wind_speed"]

            },

            "risks": {

                "flood_risk":
                flood_risk,

                "heat_risk":
                heat_risk

            },

            "alerts":
            alerts

        })

    except Exception as e:

        print("Weather Route Error:")
        print(str(e))

        return jsonify({

            "success": False,

            "message":
            "Internal server error."

        })

# =========================================================
# CHATBOT API
# =========================================================

@app.route("/chatbot", methods=["POST"])
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