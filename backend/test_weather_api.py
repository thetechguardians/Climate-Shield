import pytest
from unittest.mock import patch
import json
import os
import requests

def test_weather_api_missing_fields(client):
    response = client.post("/weather", json={"city": "Delhi"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "Please fill all fields" in data["message"]

@patch.dict(os.environ, {}, clear=True)
def test_weather_api_missing_api_key(client):
    response = client.post("/weather", json={"city": "Delhi", "state": "Delhi", "country": "IN"})
    assert response.status_code == 500
    data = response.get_json()
    assert data["success"] is False
    assert "Weather service configuration error" in data["message"]

@patch("requests.get")
@patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake_key"})
def test_weather_api_success(mock_get, client, mock_openweather_geo, mock_openweather_weather, mock_openweather_forecast):
    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self.json_data = json_data
            self.status_code = status_code
            
        def json(self):
            return self.json_data
            
        def raise_for_status(self):
            pass

    def side_effect(*args, **kwargs):
        url = args[0]
        if "geo/1.0/direct" in url:
            return MockResponse(mock_openweather_geo)
        elif "data/2.5/weather" in url:
            return MockResponse(mock_openweather_weather)
        elif "data/2.5/forecast" in url:
            return MockResponse(mock_openweather_forecast)
        return MockResponse({}, 404)

    mock_get.side_effect = side_effect

    response = client.post("/weather", json={"city": "Delhi", "state": "Delhi", "country": "IN"})
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["success"] is True
    assert data["location"]["city"] == "Delhi"
    assert data["weather"]["temperature"] == 35.0
    assert "flood_risk" in data["risks"]
    assert len(data["forecast"]) == 5
    assert len(data["alerts"]) > 0

@patch("requests.get")
@patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake_key"})
def test_weather_api_location_not_found(mock_get, client):
    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self.json_data = json_data
            self.status_code = status_code
        def json(self):
            return self.json_data
        def raise_for_status(self):
            pass

    mock_get.return_value = MockResponse([]) # Empty list means not found

    response = client.post("/weather", json={"city": "FakeCity", "state": "FakeState", "country": "XX"})
    
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert "Location not found" in data["message"]

@patch("requests.get")
@patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake_key"})
def test_weather_api_timeout(mock_get, client):
    mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

    response = client.post("/weather", json={"city": "Delhi", "state": "Delhi", "country": "IN"})
    
    assert response.status_code == 500
    data = response.get_json()
    assert data["success"] is False

@patch("requests.get")
@patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake_key"})
def test_weather_api_connection_error(mock_get, client):
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")

    response = client.post("/weather", json={"city": "Delhi", "state": "Delhi", "country": "IN"})
    
    assert response.status_code == 500
    data = response.get_json()
    assert data["success"] is False
