import requests
import os
import vonage
import json

API_KEY = os.getenv("OPENWEATHER_API_KEY")

client = vonage.Client(
    key=os.getenv("VONAGE_API_KEY"),
    secret=os.getenv("VONAGE_API_SECRET")
)

vonage_sms = vonage.Sms(client)

SMS_SUBSCRIBERS_FILE = "subscribers.json"


def load_subscribers():
    if not os.path.exists(SMS_SUBSCRIBERS_FILE):
        return []

    try:
        with open(SMS_SUBSCRIBERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        return []
    
def save_subscriber(city, phone):

    print("Saving subscriber...")
    print("Current folder:", os.getcwd())
    
    subscribers = load_subscribers()
    city = city.strip()
    phone = phone.strip()

    for subscriber in subscribers:
        if subscriber["phone"] == phone:
            return {
                "success": False,
                "message": "This phone number is already subscribed for this city."} 
        
    subscribers.append({"city": city,"phone": phone})

    with open(SMS_SUBSCRIBERS_FILE, "w", encoding="utf-8") as file:
        json.dump(subscribers, file, indent=4)
        
    print("Subscriber saved successfully")

    return {"success": True,"message":"SMS enabled successfully"}

def send_weather_alert(city, phone):

    forecast_response = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params={
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        },
        timeout=15
    )

    forecast_response.raise_for_status()
    forecast_data = forecast_response.json()
    alerts = []

    first_forecast = forecast_data["list"][0]
    temperature = first_forecast["main"]["temp"]
    humidity = first_forecast["main"]["humidity"]
    weather = first_forecast["weather"][0]["main"]
    rainfall = first_forecast.get("rain",{}).get("3h",0)
    wind_speed = round(first_forecast["wind"]["speed"] * 3.6,1)

    if rainfall >= 10:
        alerts.append("Heavy Rain Warning")

    if wind_speed >= 30:
        alerts.append("Strong Wind Warning")

    if humidity >= 85 and rainfall >= 5:
        alerts.append("Potential Flood Risk")

    if temperature >= 35:
        alerts.append("Heatwave Alert")

    if "thunderstorm" in weather.lower():
        alerts.append("Thunderstorm Alert")

    alerts = list(set(alerts))

    if not alerts:
        return {
            "success": True,
            "alerts": [],
            "message":
            "No severe weather conditions detected."
        }

    sms_text = (
        "Climate Shield Alert\n\n"
        f"Location: {city}\n"
        f"Temperature: {temperature}°C\n"
        f"Humidity: {humidity}%\n"
        f"Rainfall: {rainfall} mm\n"
        f"Wind Speed: {wind_speed} km/h\n\n"
        "Alerts:\n"
        + "\n".join(
            f"- {alert}"
            for alert in alerts
        )
    )

    response = vonage_sms.send_message({
        "from": "ClimateShield",
        "to": phone,
        "text": sms_text
    })

    print("SMS Response:")
    print(response)

    return {
        "success": True,
        "alerts": alerts,
        "sms_response": response
    }

def check_weather_and_send_alerts():

    subscribers = load_subscribers()
    print(f"Checking weather for {len(subscribers)} subscribers...")

    for subscriber in subscribers:
        city = subscriber["city"]
        phone = subscriber["phone"]
        
        try:
            result = send_weather_alert(city,phone)
            print(f"Checked alerts for {city}:",result)

        except Exception as e:
            print(f"Failed for {city}: {e}")