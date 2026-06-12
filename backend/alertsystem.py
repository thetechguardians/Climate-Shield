import os
import sys
import requests

from dotenv import load_dotenv

load_dotenv()

GIS_ALERTS_URL = os.environ.get("GIS_ALERTS_URL", "https://example.com/gis/alerts")

TRANSLATIONS = {
    "en": {
        "err_fill_fields": "Please fill all fields.",
        "err_config": "Weather service configuration error.",
        "err_location_not_found": "Location not found.",
        "err_reverse_geocode_failed": "Reverse geocoding failed.",
        "err_chatbot_unavailable": "Chatbot unavailable.",
        "alert_flood": "⚠ High Flood Risk Detected",
        "alert_heat": "🔥 Heatwave Conditions Possible",
        "alert_wildfire": "🌲 Elevated Wildfire Risk",
        "alert_cyclone": "🌀 Cyclone Risk Detected",
        "alert_drought": "☀ Drought Conditions Possible",
        "alert_none": "✅ No major climate threats detected."
    },
    "hi": {
        "err_fill_fields": "कृपया सभी फ़ील्ड भरें।",
        "err_config": "मौसम सेवा कॉन्फ़िगरेशन त्रुटि।",
        "err_location_not_found": "स्थान नहीं मिला।",
        "err_reverse_geocode_failed": "रिवर्स जियोकोडिंग विफल रही।",
        "err_chatbot_unavailable": "चैटबॉट अनुपलब्ध है।",
        "alert_flood": "⚠ उच्च बाढ़ जोखिम का पता चला",
        "alert_heat": "🔥 हीटवेव की स्थिति संभव",
        "alert_wildfire": "🌲 ऊंचा जंगल की आग का जोखिम",
        "alert_cyclone": "🌀 चक्रवात जोखिम का पता चला",
        "alert_drought": "☀ सूखे की स्थिति संभव",
        "alert_none": "✅ कोई बड़ा जलवायु खतरा नहीं पाया गया।"
    },
    "te": {
        "err_fill_fields": "దయచేసి అన్ని ఫీల్డ్‌లను పూరించండి.",
        "err_config": "వాతావరణ సేవల కాన్ఫिగరేషన్ లోపం.",
        "err_location_not_found": "ప్రాంతం కనుగొనబడలేదు.",
        "err_reverse_geocode_failed": "రివర్స్ జియోకోడింగ్ విఫలమైంది.",
        "err_chatbot_unavailable": "చాట్‌బాట్ అందుబాటులో లేదు.",
        "alert_flood": "⚠ అధిక వరద ముప్పు కనుగొనబడింది",
        "alert_heat": "🔥 వడగాల్పుల పరిస్థితులు సంభవించవచ్చు",
        "alert_wildfire": "🌲 అధిక కార్చిచ్చు ప్రమాదం",
        "alert_cyclone": "🌀 తుఫాను ప్రమాదం కనుగొనబడింది",
        "alert_drought": "☀ కరువు పరిస్థితులు సంభవించవచ్చు",
        "alert_none": "✅ పెద్ద క్లైమేట్ ముప్పులేవీ కనుగొనబడలేదు."
    },
    "ta": {
        "err_fill_fields": "தயவுசெய்து அனைத்து விவரங்களையும் நிரப்பவும்.",
        "err_config": "வானிலை சேவை உள்ளமைப்பு பிழை.",
        "err_location_not_found": "இருப்பிடம் கண்டறியப்படவில்லை.",
        "err_reverse_geocode_failed": "தலைகீழ் புவியியல் குறியீட்டு முறை தோல்வியடைந்தது.",
        "err_chatbot_unavailable": "உரையாடல் செயலி கிடைக்கவில்லை.",
        "alert_flood": "⚠ அதிக வெள்ள ஆபத்து கண்டறியப்பட்டுள்ளது",
        "alert_heat": "🔥 வெப்ப அலை நிலைமைகள் ஏற்பட வாய்ப்புள்ளது",
        "alert_wildfire": "🌲 காட்டுத்தீ ஆபத்து அதிகரித்துள்ளது",
        "alert_cyclone": "🌀 சூறாவளி ஆபத்து கண்டறியப்பட்டுள்ளது",
        "alert_drought": "☀ வறட்சி நிலைமைகள் ஏற்பட வாய்ப்புள்ளது",
        "alert_none": "✅ பெரிய காலநிலை அச்சுறுத்தல்கள் எதுவும் கண்டறியப்படவில்லை."
    },
    "kn": {
        "err_fill_fields": "ದಯವಿಟ್ಟು ಎಲ್ಲಾ ಕ್ಷೇತ್ರಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ.",
        "err_config": "ಹವಾಮಾನ ಸೇವಾ ಸಂರಚನಾ ದೋಷ.",
        "err_location_not_found": "ಸ್ಥಳ ಪತ್ತೆಯಾಗಿಲ್ಲ.",
        "err_reverse_geocode_failed": "ರಿವರ್ಸ್ ಜಿಯೋಕೋಡಿಂಗ್ ವಿಫಲವಾಗಿದೆ.",
        "err_chatbot_unavailable": "ಚಾಟ್‌ಬಾಟ್ ಲಭ್ಯವಿಲ್ಲ.",
        "alert_flood": "⚠ ಹೆಚ್ಚಿನ ಪ್ರವಾಹದ ಅಪಾಯ ಪತ್ತೆಯಾಗಿದೆ",
        "alert_heat": "🔥 ಬಿಸಿಗಾಳಿ ಪರಿಸ್ಥಿತಿಗಳು ಸಂಭವಿಸಬಹುದು",
        "alert_wildfire": "🌲 ಹೆಚ್ಚಿನ ಕಾಡಿನ ಕಿಚ್ಚಿನ ಅಪಾಯ",
        "alert_cyclone": "🌀 ಚಂಡಮಾರುತದ ಅಪಾಯ ಪತ್ತೆಯಾಗಿದೆ",
        "alert_drought": "☀ ಬರಗಾಲದ ಪರಿಸ್ಥಿತಿಗಳು ಸಂಭವಿಸಬಹುದು",
        "alert_none": "✅ ಯಾವುದೇ ಪ್ರಮುಖ ಹವಾಮಾನ ಬೆದರಿಕೆಗಳು ಪತ್ತೆಯಾಗಿಲ್ಲ."
    },
    "mr": {
        "err_fill_fields": "कृपया सर्व रकाने भरा.",
        "err_config": "हवामान सेवा कॉन्फिगरेशन त्रुटी.",
        "err_location_not_found": "ठिकाण सापडले नाही.",
        "err_reverse_geocode_failed": "रिव्हर्स जिओकोडिंग अयशस्वी झाले.",
        "err_chatbot_unavailable": "चॅटबॉट अनुपलब्ध आहे.",
        "alert_flood": "⚠ पुराचा मोठा धोका आढळला",
        "alert_heat": "🔥 उष्णतेच्या लाटेची शक्यता",
        "alert_wildfire": "🌲 वणव्याचा वाढलेला धोका",
        "alert_cyclone": "🌀 चक्रीवादळाचा धोका आढळला",
        "alert_drought": "☀ दुष्काळी परिस्थितीची शक्यता",
        "alert_none": "✅ कोणताही मोठा हवामान धोका आढळला नाही."
    }
}

def translate(key, lang="en"):
    lang_code = (lang or "en").split("-")[0].lower()
    if lang_code not in TRANSLATIONS:
        lang_code = "en"
    return TRANSLATIONS[lang_code].get(key, TRANSLATIONS["en"].get(key, ""))

def fetch_gis_alert_data():
    """
    Helper used by tests. Calls requests.get so tests can patch requests.get.
    Returns (data, status_code).

    Behavior expected by tests:
      - requests.exceptions.ConnectionError -> (None, 503)
      - requests.exceptions.Timeout         -> (None, 504)
      - On success: (response.json() or response.text, response.status_code)
      - On other exceptions: (None, 500)
    """
    try:
        resp = requests.get(GIS_ALERTS_URL, timeout=10)
        resp.raise_for_status()
        try:
            data = resp.json()
        except ValueError:
            data = resp.text
        return data, resp.status_code

    except requests.exceptions.ConnectionError:
        return None, 503

    except requests.exceptions.Timeout:
        return None, 504

    except Exception:
        return None, 500
    
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
        lang = payload.get("lang", "en")

        if not city or not state or not country:

            return jsonify({
                "success": False,
                "message": translate("err_fill_fields", lang)
            }), 400

        api_key = os.environ.get("OPENWEATHER_API_KEY")

        if not api_key:
            print("OPENWEATHER_API_KEY missing")

            return jsonify({
                "success": False,
                "message": translate("err_config", lang)
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
                "message": translate("err_location_not_found", lang)
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
                translate("alert_flood", lang)
            )

        if heat_risk_metric >= 0.6:
            calculated_alerts.append(
                translate("alert_heat", lang)
            )

        if wildfire_risk_metric >= 0.6:
            calculated_alerts.append(
                translate("alert_wildfire", lang)
            )

        if cyclone_risk_metric >= 0.6:
            calculated_alerts.append(
                translate("alert_cyclone", lang)
            )

        if drought_risk_metric >= 0.6:
            calculated_alerts.append(
                translate("alert_drought", lang)
            )

        if not calculated_alerts:
            calculated_alerts.append(
                translate("alert_none", lang)
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

@app.route("/city-suggestions", methods=["GET"])
def city_suggestions():

    query = request.args.get("q", "").strip()

    if len(query) < 2:
        return jsonify([])

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": query,
                "format": "json",
                "addressdetails": 1,
                "limit": 5,
                "countrycodes": "in"
            },
            headers={
                "User-Agent": "ClimateShield/1.0"
            },
            timeout=10
        )

        data = response.json()

        suggestions = []

        for item in data:
            address = item.get("address", {})

            if not (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("municipality")
            ):
                continue

            city_name = (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("municipality")
            )

            suggestions.append({
                "city": city_name,
                "state": address.get("state", ""),
                "country": address.get("country", "")
            })

        suggestions.sort(
            key=lambda x: (
                not x["city"].lower().startswith(query.lower()),
                x["city"].lower()
            )
        )

        print("Query:", query)
        print("Suggestions:", suggestions)

        return jsonify(suggestions)

    except Exception as e:
        print("City Suggestions Error:", e)
        return jsonify([])
    
# =========================================================
# CHATBOT API
# =========================================================

@app.route("/chatbot", methods=["POST"])
def chatbot():
    lang = "en"
    try:
        data = request.get_json(silent=True) or {}
        lang = data.get("lang", "en")
        payload, status = handle_chatbot_request(data)
        return jsonify(payload), status

    except Exception:

        return jsonify({
            "success": False,
            "message": translate("err_chatbot_unavailable", lang)
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
