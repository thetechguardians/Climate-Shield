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
import json
from datetime import timezone
from datetime import timedelta
import argparse
import sys

load_dotenv()

# Configurations
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FROM_PHONE = os.getenv("FROM_PHONE")
TO_PHONE = os.getenv("TO_PHONE")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
SMTP_SERVER = "smtp.gmail.com"
EMAIL_PORT = 587

# Mock mode: when true, external API calls and sends are skipped (useful for contributors/tests without secrets)
USE_MOCKS = os.getenv("USE_MOCKS", "false").lower() in ("1", "true", "yes")
# Allow auto-send (skip interactive confirmation) via env var or CLI flag
AUTO_SEND_ENV = os.getenv("AUTO_SEND", "false").lower() in ("1", "true", "yes")
AUTO_SEND = False

# Weather provider: 'openweather' (default, requires API key) or 'open_meteo' (no API key)
WEATHER_PROVIDER = os.getenv("WEATHER_PROVIDER", "openweather").lower()

# Auto-enable mock mode only if the chosen provider requires a key and the key is missing.
if WEATHER_PROVIDER.startswith("openweather"):
    if not OPENWEATHER_API_KEY:
        if not USE_MOCKS:
            print("[INFO] OPENWEATHER_API_KEY is not set and WEATHER_PROVIDER=openweather. Enabling mock mode so the program can run without API keys.")
        USE_MOCKS = True

# Risk Thresholds
FLOOD_RISK_THRESHOLD = 0.7
HEAT_RISK_THRESHOLD = 0.75

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

#Configurations
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FROM_PHONE = os.getenv("FROM_PHONE")
TO_PHONE = os.getenv("TO_PHONE")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
SMTP_SERVER = "smtp.gmail.com"
EMAIL_PORT = 587

# Risk Thresholds
FLOOD_RISK_THRESHOLD = 0.7
HEAT_RISK_THRESHOLD = 0.75


def fetch_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if "main" not in data:
        print("Weather API Error:", data)
        return None

    return data


def calculate_flood_risk(weather_data):
    rainfall = weather_data.get("rain", {}).get("1h", 0)
    humidity = weather_data["main"]["humidity"]
    wind_speed = weather_data["wind"]["speed"]

   
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


def forecast_temperature(history_df):
    model = Prophet()
    model.fit(history_df)

    future = model.make_future_dataframe(periods=3)
    forecast = model.predict(future)

    return forecast[['ds', 'yhat']].tail(3)


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
            f"Risk score: {flood_risk}. Avoid low-lying areas."
        )

    if heat_risk > HEAT_RISK_THRESHOLD:
        explanation.append(
            f"Heatwave alert triggered due to high temperature and humidity. "
            f"Risk score: {heat_risk}. Stay hydrated and avoid outdoor activity."
        )

    return "\n".join(explanation)


def send_email(subject, message):
    if USE_MOCKS:
        print("[MOCK] send_email called")
        print("Subject:", subject)
        print(message)
        return

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
    if USE_MOCKS:
        print("[MOCK] send_sms called")
        print(message)
        return

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(body=message, from_=FROM_PHONE, to=TO_PHONE)


def main(auto_send: bool = False):
    global AUTO_SEND
    AUTO_SEND = AUTO_SEND_ENV or auto_send

    print(f"[INFO] Provider={WEATHER_PROVIDER} | USE_MOCKS={USE_MOCKS} | AUTO_SEND={AUTO_SEND}")

    try:
        city = input("Enter campus city: ")
    except Exception:
        print("No input available; exiting.")
        return

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

        # Confirmation before sending real alerts
        if USE_MOCKS:
            # In mock mode, calls are safe and will print instead of sending
            send_email("Campus Climate Risk Alert", explanation)
            send_sms(explanation)
        else:
            if AUTO_SEND:
                send_email("Campus Climate Risk Alert", explanation)
                send_sms(explanation)
                print("Alerts sent (AUTO_SEND=true).")
            else:
                try:
                    resp = input("Send alerts? (y/n): ").strip().lower()
                except Exception:
                    resp = "n"

                if resp in ("y", "yes"):
                    send_email("Campus Climate Risk Alert", explanation)
                    send_sms(explanation)
                    print("Alerts sent.")
                else:
                    print("Alerts not sent (user declined).")
    else:
        print("No major risk detected.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Climate-Shield alert system")
    parser.add_argument("--yes-send", dest="yes_send", action="store_true",
                        help="Automatically confirm sending alerts (skip interactive prompt)")
    args = parser.parse_args()
    try:
        main(auto_send=args.yes_send)
    except KeyboardInterrupt:
        print("Interrupted by user")
        sys.exit(0)