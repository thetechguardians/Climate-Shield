# 🌍 Climate-Shield

> **AI-driven real-time flood and heat risk alert system with crisis mapping and intelligent notifications**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)

## Overview

Climate-Shield is an intelligent weather monitoring and alert system designed to detect and notify users about potential flood and heat wave risks in real-time. Using advanced forecasting models and multi-channel alert delivery, it helps communities stay informed and safe during extreme weather events.

### Key Features

✨ **Core Capabilities:**
- 🚨 **Real-time Risk Detection**: Continuous monitoring of flood and heat wave risks using live weather data
- 📊 **Predictive Forecasting**: Prophet-based time series forecasting for accurate risk prediction
- 💬 **Intelligent Chatbot**: AI-powered chatbot providing information about weather disasters
- 📲 **Multi-channel Alerts**: SMS and email notifications via Twilio
- 🔐 **Configuration Management**: Secure environment-based configuration

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.8+ |
| **Weather Data** | OpenWeatherMap API |
| **Forecasting** | Facebook Prophet |
| **Notifications** | Twilio (SMS/Email) |
| **Data Processing** | Pandas, NumPy |
| **Chatbot** | Wikipedia API |

## Project Structure

```
Climate-Shield/
├── backend/
│   ├── alertsystem.py          # Main alert detection & notification engine
│   └── .env                    # Configuration (see setup below)
├── AI chatbot/
│   └── chatbot.py              # Interactive weather disaster chatbot
├── README.md                   # This file
├── LICENSE                     # Project license
└── .gitignore                   # Git configuration
```

## Prerequisites

Before you begin, ensure you have the following:

### Required Accounts & APIs
1. **Twilio Account**: [Sign up here](https://www.twilio.com/en-us)
   - Account SID
   - Auth Token
   - Phone number (for SMS)

2. **OpenWeatherMap Account**: [Sign up here](https://home.openweathermap.org/users/sign_in)
   - API Key

3. **Gmail Account** (for email alerts)
   - App password (if 2FA enabled)

### System Requirements
- Python 3.8 or higher
- pip (Python package manager)
- Windows/Linux/macOS

## Installation

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd Climate-Shield
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install requests pandas numpy prophet twilio python-dotenv
```

## Configuration

### Step 1: Create `.env` File
In the `backend/` directory, create a `.env` file with the following variables:

```env
# OpenWeatherMap Configuration
OPENWEATHER_API_KEY=your_openweathermap_api_key

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
FROM_PHONE=+1234567890          # Your Twilio phone number
TO_PHONE=+0987654321            # Recipient phone number

# Email Configuration
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
```

### Step 2: Update Configuration Values
1. Get your API keys from respective platforms
2. Update all values in `backend/.env`
3. Ensure the file is in `.gitignore` (never commit credentials)

## Usage

### Running the Alert System
```bash
cd backend
python alertsystem.py
```

The system will:
- Fetch real-time weather data
- Calculate flood and heat wave risks
- Send alerts via SMS/Email if thresholds are exceeded
- Continue monitoring at regular intervals

**Risk Thresholds:**
- Flood Risk: > 0.7
- Heat Risk: > 0.75

### Running the Chatbot
```bash
cd "AI chatbot"
python chatbot.py
```

**Chatbot Features:**
- Ask questions about floods, heat waves, climate change
- Get Wikipedia-powered summaries
- Type `exit` to quit

Example interactions:
```
You: What is a heat wave?
Bot: A heat wave is a prolonged period of excessively hot weather...

You: Tell me about flooding
Bot: Flooding is an overflow of water onto normally dry land...

You: exit
```

## How It Works

### Alert System Architecture

```
Weather Data (OpenWeatherMap)
        ↓
Fetch Weather Information
        ↓
Risk Calculation
├─ Flood Risk: Rainfall + Humidity + Wind
└─ Heat Risk: Temperature + Humidity + UV Index
        ↓
Threshold Comparison
        ↓
Send Alerts (SMS/Email via Twilio)
        ↓
Continuous Monitoring
```

### Risk Calculation

**Flood Risk Score:**
- 50% weight: Rainfall intensity
- 30% weight: Humidity level
- 20% weight: Wind speed

**Heat Risk Score:**
- 40% weight: Temperature
- 35% weight: Humidity
- 25% weight: Wind speed

## API References

- [OpenWeatherMap API Docs](https://openweathermap.org/api)
- [Twilio SMS API](https://www.twilio.com/docs/sms)
- [Facebook Prophet Docs](https://facebook.github.io/prophet/)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `API key invalid` | Verify your API key in `.env` file |
| `Connection timeout` | Check internet connection and API rate limits |
| `SMS not received` | Verify phone numbers in `.env` (include country code) |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` or install packages individually |
| `Weather data not found` | Ensure city name is correct in the code |

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests to improve the project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact & Support

For questions or support, please open an issue in the repository.

---

**Stay Safe, Stay Informed! 🌦️**
