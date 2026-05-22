# Climate-Shield

Lightweight web frontend + two small Flask backends that provide weather risk analysis and a rule-based chatbot.

![License](https://img.shields.io/badge/license-MIT-blue)

## What this repository contains

- Frontend static site: [Frontend/Index.html](Frontend/Index.html) and analysis workspace at [Frontend/Analysis/analysis.html](Frontend/Analysis/analysis.html). The frontend is plain HTML/CSS/JS and includes a small chatbot widget.
- Weather alert API: [backend/alertsystem.py](backend/alertsystem.py) — a Flask app that fetches weather data from the Open‑Meteo public APIs and computes simple flood/heat risk scores.
- Chatbot API: [AI-chatbot/chatbot.py](AI-chatbot/chatbot.py) — a tiny rule-based chatbot with a Flask endpoint used by the frontend.
- Project license: [LICENSE](LICENSE)
- Requirements manifest: [requirements.txt](requirements.txt)

## Technology stack

- Frontend: HTML, CSS, vanilla JavaScript
- Backend: Python 3.8+ with Flask and Flask-Cors
- HTTP requests from backends use the `requests` library

The project does not require any external paid services by default — the alert system uses Open‑Meteo public endpoints (no API key required) and the chatbot is local and rule-based.

## Minimal prerequisites

- Python 3.8 or newer
- pip

## Install dependencies

Create and activate a virtual environment (recommended), then install the requirements:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Run the services

1. Start the weather alert API (default port 5000):

```bash
python backend/alertsystem.py
```

The endpoint is available at http://127.0.0.1:5000/weather (expects POST JSON with `city`, `state`, and `country`).

2. Start the chatbot API (default port 5001):

```bash
python AI-chatbot/chatbot.py --mode api --host 127.0.0.1 --port 5001
```

Health: http://127.0.0.1:5001/health

3. Open the frontend

- Easiest: open `Frontend/Index.html` in your browser (file://) — it calls the two local Flask APIs above.
- If you prefer a local web server (recommended for AJAX requests), serve the `Frontend` folder, for example:

```bash
cd Frontend
python -m http.server 8000
# then open http://localhost:8000
```

## How to use the analysis page

- Open [Frontend/Analysis/analysis.html](Frontend/Analysis/analysis.html).
- Enter a `city`, `state`, and `country` (e.g., `Mumbai`, `Maharashtra`, `India`) and click Analyze.
- The page calls the backend `/weather` route and displays risk scores and alerts.

## Notes and limitations

- The alert system uses Open‑Meteo public APIs (geocoding + forecast). No API key is required.
- The chatbot (`AI-chatbot/chatbot.py`) is rule-based and runs locally — it does not call external AI services.
- There are no Twilio/email integrations or forecasting (Prophet) code in the current workspace; any references to those tools in older docs were removed to match the actual code.

## Project structure (relevant files)

```
Climate-Shield/
├─ Frontend/
│  ├─ Index.html
│  ├─ style.css
│  ├─ script.js
│  ├─ chatbot.js
│  └─ Analysis/
│     ├─ analysis.html
│     ├─ analysis.css
│     └─ analysis.js
├─ backend/
│  └─ alertsystem.py
├─ AI-chatbot/
│  └─ chatbot.py
├─ requirements.txt
└─ LICENSE
```

## Troubleshooting

- ModuleNotFoundError: verify your virtual environment is active and run `pip install -r requirements.txt`.
- Backend not reachable from frontend: if you open the HTML directly (file://), some browsers may block fetch; prefer serving `Frontend` with `python -m http.server`.
- If ports 5000/5001 are already in use, run the services on different ports (chatbot supports `--port`).

## Contributing

If you want to improve the UI, add forecasting, or wire notifications, open an issue or submit a PR. Keep changes focused and include a short README update if you add new external dependencies or configuration.

---

Licensed under the MIT License. See [LICENSE](LICENSE) for details.

