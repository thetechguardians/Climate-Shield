import requests
import pandas as pd
import numpy as np
from datetime import datetime
from prophet import Prophet
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()


OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FROM_PHONE = os.getenv("FROM_PHONE")
TO_PHONE = os.getenv("TO_PHONE")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")

# ===============================
# CONFIGURATION
# ===============================
SMTP_SERVER = "smtp.gmail.com"
EMAIL_PORT = 587

# Risk Thresholds
FLOOD_RISK_THRESHOLD = 0.7
HEAT_RISK_THRESHOLD = 0.75

# ===============================
# 1️⃣ DATA LAYER
# ===============================


def fetch_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if "main" not in data:
        print("Weather API Error:", data)
        return None

    return data

# ===============================
# 2️⃣ ML MODEL LAYER
# ===============================

def calculate_flood_risk(weather_data):
    rainfall = weather_data.get("rain", {}).get("1h", 0)
    humidity = weather_data["main"]["humidity"]
    wind_speed = weather_data["wind"]["speed"]

    # Simple weighted scoring model
    risk_score = (
        0.5 * min(rainfall / 50, 1) +
        0.3 * (humidity / 100) +
        0.2 * min(wind_speed / 30, 1)
    )

    return round(risk_score, 2)

def calculate_heat_risk(weather_data):
    temp = weather_data["main"]["temp"]
    humidity = weather_data["main"]["humidity"]

    heat_index = temp + (0.33 * humidity) - 4
    risk_score = min(heat_index / 50, 1)

    return round(risk_score, 2)

# Optional: Future Forecasting using Prophet
def forecast_temperature(history_df):
    model = Prophet()
    model.fit(history_df)

    future = model.make_future_dataframe(periods=3)
    forecast = model.predict(future)

    return forecast[['ds', 'yhat']].tail(3)

# ===============================
# 3️⃣ AI EXPLANATION LAYER
# ===============================

def generate_explanation(flood_risk, heat_risk):
    explanation = []

    if flood_risk > FLOOD_RISK_THRESHOLD:
        explanation.append(
            f"Flood alert triggered due to high rainfall and humidity levels. "
            f"Risk score: {flood_risk}. Avoid low-lying areas."
        )

    if heat_risk > HEAT_RISK_THRESHOLD:
        explanation.append(
            f"Heatwave alert triggered due to high temperature and humidity. "
            f"Risk score: {heat_risk}. Stay hydrated and avoid outdoor activity."
        )

    return "\n".join(explanation)

# ===============================
# 4️⃣ ALERT SYSTEM
# ===============================

def send_email(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS

    server = smtplib.SMTP(SMTP_SERVER, EMAIL_PORT)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
    server.quit()

def send_sms(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(body=message, from_=FROM_PHONE, to=TO_PHONE)

# ===============================
# 5️⃣ MAIN EXECUTION
# ===============================

def main():
    city = input("Enter campus city: ")

    weather_data = fetch_weather(city)
    weather_data = fetch_weather(city)

    if weather_data is None:
        print("Failed to fetch weather data.")
        return

    flood_risk = calculate_flood_risk(weather_data)
    heat_risk = calculate_heat_risk(weather_data)

    print(f"Flood Risk Score: {flood_risk}")
    print(f"Heat Risk Score: {heat_risk}")

    explanation = generate_explanation(flood_risk, heat_risk)

    if explanation:
        print("\nALERT TRIGGERED\n")
        print(explanation)

        send_email("Campus Climate Risk Alert", explanation)
        send_sms(explanation)
    else:
        print("No major risk detected.")

if __name__ == "__main__":
    main()