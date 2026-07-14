import pytest
from backend.alertsystem import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_openweather_geo():
    return [
        {
            "name": "Delhi",
            "lat": 28.6139,
            "lon": 77.2090,
            "country": "IN",
            "state": "Delhi"
        }
    ]

@pytest.fixture
def mock_openweather_weather():
    return {
        "main": {
            "temp": 35.0,
            "humidity": 40
        },
        "wind": {
            "speed": 5.0
        },
        "rain": {
            "1h": 0
        }
    }

@pytest.fixture
def mock_openweather_forecast():
    return {
        "list": [
            {
                "dt_txt": "2023-10-01 12:00:00",
                "main": {
                    "temp": 36.0,
                    "humidity": 45
                },
                "wind": {
                    "speed": 4.5
                },
                "rain": {
                    "3h": 0
                }
            }
        ] * 40  # Just enough items to simulate API response
    }
