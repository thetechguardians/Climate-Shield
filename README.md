# 🌍 Climate Shield

AI-driven real-time climate risk analysis platform for detecting flood and heatwave threats using live weather intelligence.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-black)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

---

# 🚀 Live Demo

🌐 https://climate-shield.onrender.com

---

# 📌 Overview

Climate Shield is a lightweight climate intelligence platform that combines:

* 🌦 Real-time weather monitoring
* ⚠ Flood and heatwave risk analysis
* 🤖 AI-powered climate awareness chatbot
* 📊 Modern analytics dashboard
* 🌍 Location-based weather insights

Users can enter:

* City
* State
* Country

and instantly receive:

* Live weather data
* Flood risk score
* Heatwave risk score
* Climate alerts
* Safety guidance

---

# ✨ Features

## 🌦 Real-Time Weather Monitoring

Climate Shield fetches live weather data using the OpenWeatherMap API and displays:

* Temperature
* Humidity
* Rainfall
* Wind Speed

---

## ⚠ Climate Risk Analysis

The backend computes:

### Flood Risk

Based on:

* Rainfall
* Humidity
* Wind speed

### Heatwave Risk

Based on:

* Temperature
* Humidity

---

## 🚨 Smart Alert System

The platform automatically generates alerts such as:

* ⚠ Flood Risk Detected
* ☀ Heatwave Risk Detected
* ✅ No major climate risks detected

---

## 🤖 ClimateBot AI Assistant

Climate Shield includes an integrated AI chatbot that provides:

* Flood awareness
* Heatwave precautions
* Cyclone safety guidance
* Climate change information
* Disaster preparedness suggestions

The chatbot is lightweight and rule-based.

---

# 🖥 Frontend

Built using:

* HTML5
* CSS3
* Vanilla JavaScript

Frontend features:

* Glassmorphism UI
* Responsive design
* Animated result cards
* Interactive chatbot widget
* Live climate analysis

---

# ⚙ Backend

Powered by:

* Python
* Flask
* Flask-CORS

Backend responsibilities:

* Weather API communication
* Risk calculations
* Climate alert generation
* Chatbot API responses
* Frontend serving

---

# 🧠 Tech Stack

| Technology         | Purpose              |
| ------------------ | -------------------- |
| Python             | Backend logic        |
| Flask              | API server           |
| Flask-CORS         | Cross-origin support |
| HTML/CSS/JS        | Frontend             |
| OpenWeatherMap API | Live weather data    |
| Render             | Deployment           |

---

# 📂 Project Structure

```bash
Climate-Shield/
├── AI-chatbot/
│   └── chatbot.py
│
├── backend/
│   └── alertsystem.py
│
├── Frontend/
│   ├── index.html
│   ├── chatbot.js
│   ├── script.js
│   ├── style.css
│   │
│   └── Analysis/
│       ├── analysis.html
│       ├── analysis.css
│       └── analysis.js
│
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── requirements.txt
```

---

# 🛠 Installation Guide

## ⭐ Star the Repository

## 1️⃣ Clone Repository

```bash
git clone https://github.com/thetechguardians/Climate-Shield.git

cd Climate-Shield
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment Variables

Create a `.env` file in the root directory:

```env
OPENWEATHER_API_KEY=your_api_key_here
```

Get your free API key from:

https://openweathermap.org/api

---

## 5️⃣ Run Backend

```bash
python backend/alertsystem.py
```

Backend runs on:

```text
http://127.0.0.1:5000
```

---

## 6️⃣ Open Frontend

Open:

```text
Frontend/index.html
```

OR serve locally:

```bash
cd Frontend

python -m http.server 8000
```

---

# 🌐 API Endpoints

## Weather Analysis

### POST `/weather`

### Request

```json
{
  "city": "Guwahati",
  "state": "Assam",
  "country": "India"
}
```

### Response

```json
{
  "success": true,
  "weather": {
    "temperature": 29,
    "humidity": 83,
    "rainfall": 5,
    "wind_speed": 12
  },
  "risks": {
    "flood_risk": 0.62,
    "heat_risk": 0.41
  },
  "alerts": [
    "⚠ Flood Risk Detected"
  ]
}
```

---

## Chatbot API

### POST `/chatbot`

### Request

```json
{
  "message": "What precautions should I take during floods?"
}
```

### Response

```json
{
  "success": true,
  "response": "You should avoid low-lying areas during floods."
}
```

---

# 🚀 Deployment on Render

## Build Command

```bash
pip install -r requirements.txt
```

## Start Command

```bash
gunicorn backend.alertsystem:app
```

---

# 🔐 Environment Variables

| Variable            | Description            |
| ------------------- | ---------------------- |
| OPENWEATHER_API_KEY | OpenWeatherMap API Key |

---

# 📈 Future Improvements

* 🌧 Rain prediction forecasting
* 📍 Interactive GIS climate maps
* 📲 SMS / Email emergency alerts
* 🛰 Satellite weather integration
* 🧠 Machine learning risk prediction
* 🌎 Multi-language support

---

# 🤝 Contributing

Contributions are welcome.

Please read:

```text
CONTRIBUTING.md
```

before submitting pull requests.

---

# 🛡 License

This project is licensed under the MIT License.

---

# 👨‍💻 Authors

Developed by Team Climate Shield.
- [@Vikrant0207](https://github.com/Vikrant0207)

---

## 📞 Support & Community

### 🆘 Need Help?
- 💬 **Discussions**: [GitHub Discussions](https://github.com/thetechguardians/Climate-Shield/discussions)
- 🐛 **Bug Reports**: [Open an Issue](https://github.com/thetechguardians/Climate-Shield/issues)
- 📧 **Direct Contact**: Create an issue for any questions

### 🌟 Stay Connected
- 📱 **Instagram**: [@vikrant.__07](https://www.instagram.com/vikrant.__07/)
- 💼 **LinkedIn**: [Vikrant Kumar Mehta](www.linkedin.com/in/vikrant-kumar-mehta)
- 🐙 **GitHub**: [@Vikrant0207](https://github.com/Vikrant0207)

---

# 🌍 Vision

Climate Shield aims to make climate risk awareness:

* Fast
* Accessible
* Intelligent
* Easy to understand

for communities, students, researchers, and emergency responders.

---

# ⭐ Show Your Support

If this project helped you, please consider:
- ⭐ **Starring** this repository
- 🍴 **Forking** it to contribute
- 📢 **Sharing** it with others
- 💖 **Following** for more amazing projects
- 🛠 **Contribute** improvements

---
