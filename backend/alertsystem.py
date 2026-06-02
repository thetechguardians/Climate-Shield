import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# FIX FOR ISSUE #83: Exception Handling
# ==========================================
def fetch_gis_alert_data():
    """
    Fetches external GIS climate data streams.
    Implements try-except blocks to prevent backend crashes.
    """
    GIS_API_URL = "https://external-gis-source.com"
    
    try:
        # Added a 5-second timeout parameter to prevent hanging
        response = requests.get(GIS_API_URL, timeout=5)
        
        # Triggers an HTTP error if the remote server answers with a 4xx or 5xx code
        response.raise_for_status()
        
        # Safely parse JSON data payload
        return response.json(), 200

    except requests.exceptions.Timeout:
        # Handles Case 2: Gateway Timeout (504)
        return {"error": "External GIS service timed out. Please try again."}, 504

    except (requests.exceptions.RequestException, ValueError):
        # Handles Case 1 & 3: Connection drops or corrupt data formatting (503)
        return {"error": "External GIS service is unavailable or returned an invalid response."}, 503

# ==========================================
# Core App Weather Routing Restored
# ==========================================
@app.route('/weather', methods=['POST'])
def get_weather_insights():
    try:
        payload = request.get_json() or {}
        city = payload.get("city", "").strip()
        state = payload.get("state", "").strip()
        country = payload.get("country", "").strip()

        if not city or not state or not country:
            return jsonify({"success": False, "message": "Please fill all fields."}), 400

        # Run exception-handled GIS sub-routine fetch
        gis_data, gis_status = fetch_gis_alert_data()
        
        # Sample live values (in a real deployment these would come from a weather API)
        temp_val = 28.5
        humid_val = 65
        rain_val = 12.0
        wind_val = 15.4

        # Normalize risk metrics to floats between 0.0 and 1.0 as expected by the frontend
        flood_risk_metric = min(1.0, rain_val / 100.0)
        heat_risk_metric = min(1.0, max(0.0, (temp_val - 15.0) / 40.0))
        wildfire_risk_metric = 0.05  # placeholder low probability
        cyclone_risk_metric = 0.02
        drought_risk_metric = max(0.0, 1.0 - (humid_val / 100.0))

        calculated_alerts = ["Regional advisory: Stay updated on weather tracking changes."]
        if gis_status != 200:
            calculated_alerts.append(f"GIS Notice: {gis_data.get('error')}")

        # Provide a 5-day forecast sample to satisfy frontend chart rendering
        from datetime import datetime, timedelta
        forecast = []
        for i in range(5):
            day_temp = temp_val + (i - 2) * 1.5
            day_humidity = max(10, humid_val - (i - 2) * 2)
            day_rain = max(0.0, rain_val + (i - 2) * 1.2)
            forecast.append({
                "date": (datetime.utcnow() + timedelta(days=i)).isoformat(),
                "temperature": round(day_temp, 1),
                "humidity": int(day_humidity),
                "rainfall": round(day_rain, 1),
                "wind_speed": round(wind_val, 1),
                "risks": {
                    "flood_risk": round(min(1.0, day_rain / 100.0), 3),
                    "heat_risk": round(min(1.0, max(0.0, (day_temp - 15.0) / 40.0)), 3),
                    "wildfire_risk": round(wildfire_risk_metric, 3),
                    "cyclone_risk": round(cyclone_risk_metric, 3),
                    "drought_risk": round(max(0.0, 1.0 - (day_humidity / 100.0)), 3)
                }
            })

        # Provide a latitude/longitude fallback so the frontend map can center
        lat = 26.1445
        lon = 91.7362

        return jsonify({
            "success": True,
            "location": {"city": city, "state": state, "country": country, "latitude": lat, "longitude": lon},
            "weather": {
                "temperature": temp_val,
                "humidity": humid_val,
                "rainfall": rain_val,
                "wind_speed": wind_val
            },
            "risks": {
                "flood_risk": round(flood_risk_metric, 3),
                "heat_risk": round(heat_risk_metric, 3),
                "wildfire_risk": round(wildfire_risk_metric, 3),
                "cyclone_risk": round(cyclone_risk_metric, 3),
                "drought_risk": round(drought_risk_metric, 3)
            },
            "forecast": forecast,
            "alerts": calculated_alerts,
            "demo_mode": gis_status != 200
        }), 200

    except Exception as general_err:
        return jsonify({"success": False, "message": f"Server processing error: {str(general_err)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
