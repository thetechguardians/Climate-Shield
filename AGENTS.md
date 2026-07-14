# AGENTS.md - Climate Shield

## Quick Start

```bash
# Backend (Flask, serves frontend + API)
python backend/alertsystem.py
# Runs on http://127.0.0.1:5000

# Frontend dev server (static only, no API)
npm run dev
# Runs on http://127.0.0.1:8080
```

## Setup Requirements

1. Copy `.env.example` to `.env` and add your `OPENWEATHER_API_KEY`
2. Install Python deps: `pip install flask flask-cors requests python-dotenv gunicorn`
3. Frontend dev: `npm install` (optional, only for `npm run dev`)

## Architecture

```
Frontend (HTML/CSS/JS)  →  Flask backend (alertsystem.py)  →  OpenWeatherMap API
                              ↓
                         AI-chatbot/chatbot.py (rule-based, no LLM)
```

- `backend/alertsystem.py` is the **single entrypoint** — serves frontend files AND API routes
- Chatbot is imported into backend via `sys.path.insert` (see `backend/alertsystem.py:68-71`)
- Frontend resolves API URL dynamically based on hostname (`Frontend/script.js:68-84`)

## Key Files

| File | Role |
|------|------|
| `backend/alertsystem.py` | Flask app, all API routes, risk calculations, frontend serving |
| `AI-chatbot/chatbot.py` | Rule-based chatbot with topic detection |
| `Frontend/script.js` | Main frontend logic, API calls, Leaflet map, Chart.js |
| `Frontend/Analysis/analysis.js` | Analysis page with charts and maps |
| `backend/test_alertsystem.py` | Only test file (pytest, tests GIS alert error handling) |

## API Routes

- `POST /weather` — city/state/country → weather data + risk scores + forecast
- `POST /chatbot` — message + optional context → chatbot response
- `POST /reverse-geocode` — lat/lon → city/state/country
- `GET /city-suggestions?q=` — autocomplete (limited to India: `countrycodes: in`)

## Risk Thresholds

Defined in `backend/alertsystem.py:104-108`:
- Flood: 0.65, Heat: 0.75, Wildfire: 0.65, Cyclone: 0.60, Drought: 0.70

Alerts trigger when score ≥ 0.6 (hardcoded in `/weather` route, differs from constants).

## Testing

```bash
pytest backend/test_alertsystem.py
```

No test runner config, no CI workflows, no linting setup. Tests use `unittest.mock.patch`.

## Gotchas

- **No `requirements.txt`** — README references it but it doesn't exist. Install deps manually.
- **Duplicate `fetch_gis_alert_data`** — defined twice in `alertsystem.py` (lines 11 and 178). Second definition wins.
- **Frontend serves from Flask** — when running `python backend/alertsystem.py`, open `http://127.0.0.1:5000` (not the HTML file directly).
- **Chatbot port** — standalone chatbot runs on port 5001, but when imported into backend it uses the backend's port.
- **City suggestions** — hardcoded to India (`countrycodes: "in"` in `alertsystem.py:628`).

## Installed Skills

| Skill | Use Case |
|-------|----------|
| `conventional-commit` | Write standardized git commit messages following the Conventional Commits spec |
| `flask-api-development` | Build Flask routes, blueprints, auth, and request/response handling |
| `modern-javascript-patterns` | Use ES6+ features like async/await, destructuring, modules, and functional patterns |
| `python-design-patterns` | Structure Python code with KISS, single responsibility, and composition principles |
| `python-observability` | Add structured logging, metrics, and tracing to debug production issues |

## Deployment (Render)

```yaml
buildCommand: pip install -r requirements.txt
startCommand: gunicorn backend.alertsystem:app
```

Requires `gunicorn` in dependencies and `OPENWEATHER_API_KEY` env var.
