import pytest
import requests
from unittest.mock import patch
from backend.alertsystem import fetch_gis_alert_data, app

@pytest.fixture
def client():
    app.testing = True
    
    with app.test_client() as client:
        yield client

@patch.dict('os.environ', {}, clear=True)
def test_missing_api_key_returns_500(client):
    response = client.post("/weather", json={"city": "DummyCity", "state": "DummyState", "country": "DummyCountry"})
    assert response.status_code == 500

@patch('requests.get')
def test_gis_api_down_returns_503(mock_get):
    """Test Case 1: External API Offline (503 Service Unavailable)"""
    mock_get.side_effect = requests.exceptions.ConnectionError()
    response, status_code = fetch_gis_alert_data()
    assert status_code == 503

@patch('requests.get')
def test_gis_api_timeout_returns_504(mock_get):
    """Test Case 2: External API Timeout (504 Gateway Timeout)"""
    mock_get.side_effect = requests.exceptions.Timeout()
    response, status_code = fetch_gis_alert_data()
    assert status_code == 504

def test_weather_missing_fields_returns_400(client):
    response = client.post("/weather", json={})
    assert response.status_code == 400

@patch.dict('os.environ', {'OPENWEATHER_API_KEY': 'dummy_key'})
@patch('requests.get')
def test_location_not_found_returns_404(mock_get, client):
    mock_response = mock_get.return_value
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = []
    
    response = client.post("/weather", json={"city": "dummyCity", "state": "dummyState", "country": "dummyCountry"})
    assert response.status_code == 404