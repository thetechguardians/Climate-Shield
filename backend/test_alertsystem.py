import pytest
import requests
from unittest.mock import patch
from alertsystem import fetch_gis_alert_data

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
