import sys
import os
import pytest
from unittest.mock import patch

# Resolve the AI-chatbot folder path and inject it into system path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "AI-chatbot"))

from backend.alertsystem import app, translate
from chatbot import get_chatbot_translation, handle_chatbot_request, generate_response

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_translate_helper_direct():
    """Test the translation helper directly on the backend"""
    # Test valid translations
    assert translate("err_fill_fields", "en") == "Please fill all fields."
    assert translate("err_fill_fields", "hi") == "कृपया सभी फ़ील्ड भरें।"
    assert translate("err_fill_fields", "es") == "Por favor, complete todos los campos."
    assert translate("err_fill_fields", "fr") == "Veuillez remplir tous les champs."
    
    # Test fallback for unsupported language
    assert translate("err_fill_fields", "it") == "Please fill all fields."
    # Test fallback for missing translation key
    assert translate("non_existent_key", "es") == ""

def test_chatbot_translate_helper():
    """Test get_chatbot_translation helper directly"""
    # Test levels
    assert get_chatbot_translation("levels.low", "en") == "Low"
    assert get_chatbot_translation("levels.low", "hi") == "कम"
    assert get_chatbot_translation("levels.low", "es") == "Bajo"
    assert get_chatbot_translation("levels.low", "fr") == "Faible"
    
    # Test fallback for unsupported language
    assert get_chatbot_translation("levels.low", "it") == "Low"

def test_chatbot_response_localization():
    """Test chatbot greeting and general topic response localization"""
    # Greetings
    hi_greets = ["नमस्ते 👋 मैं क्लाइमेटबॉट हूँ।", "नमस्ते। आज मैं आपकी क्या मदद कर सकता हूँ?", "क्लाइमेट शील्ड की ओर से बधाई 🌍"]
    es_greets = ["Hola 👋 Soy ClimateBot.", "Hola. ¿Cómo puedo ayudarte hoy?", "Saludos desde Climate Shield 🌍"]
    fr_greets = ["Bonjour 👋 Je suis ClimateBot.", "Bonjour. Comment puis-je vous aider aujourd'hui ?", "Salutations de Climate Shield 🌍"]
    
    # Test generate_response for greetings in different languages
    res_en = generate_response("hello", lang="en")
    assert any(g in res_en for g in ["Hello", "Hi", "Greetings"])
    
    res_hi = generate_response("नमस्ते", lang="hi")
    assert res_hi in hi_greets
    
    res_es = generate_response("hola", lang="es")
    assert res_es in es_greets
    
    res_fr = generate_response("bonjour", lang="fr")
    assert res_fr in fr_greets

    # Test topic answers (e.g. flood precautions)
    res_flood_en = generate_response("what precautions during flood?", lang="en")
    # Starters for en
    assert any(s in res_flood_en for s in ["important question", "know", "explain", "Sure"])
    # Knowledge items for en flood precautions
    assert any(k in res_flood_en for k in ["avoid low-lying", "emergency supplies", "higher ground"])

    res_flood_hi = generate_response("बाढ़ के दौरान सावधानियां", lang="hi")
    assert any(s in res_flood_hi for s in ["प्रश्न", "विषय", "जानता", "समझा", "ज़रूर"])
    assert any(k in res_flood_hi for k in ["निचले इलाकों", "दस्तावेज तैयार", "ऊंचे स्थानों"])

def test_chatbot_endpoint_localization(client):
    """Test the /chatbot endpoint logic with lang parameter"""
    # Test English chatbot query
    resp_en = client.post("/chatbot", json={
        "message": "hello",
        "lang": "en"
    })
    assert resp_en.status_code == 200
    data_en = resp_en.get_json()
    assert data_en["success"] is True
    assert any(g in data_en["response"] for g in ["Hello", "Hi", "Greetings"])

    # Test Hindi chatbot query
    resp_hi = client.post("/chatbot", json={
        "message": "नमस्ते",
        "lang": "hi"
    })
    assert resp_hi.status_code == 200
    data_hi = resp_hi.get_json()
    assert data_hi["success"] is True
    hi_greets = ["नमस्ते 👋 मैं क्लाइमेटबॉट हूँ।", "नमस्ते। आज मैं आपकी क्या मदद कर सकता हूँ?", "क्लाइमेट शील्ड की ओर से बधाई 🌍"]
    assert data_hi["response"] in hi_greets

    # Test Fallback chatbot query
    resp_it = client.post("/chatbot", json={
        "message": "hello",
        "lang": "it"
    })
    assert resp_it.status_code == 200
    data_it = resp_it.get_json()
    assert data_it["success"] is True
    assert any(g in data_it["response"] for g in ["Hello", "Hi", "Greetings"])

@patch('requests.get')
def test_weather_endpoint_fill_fields(mock_get, client):
    """Test field validation translations via the weather route"""
    # Empty fields should fail with localized message
    resp_en = client.post("/weather", json={
        "city": "",
        "state": "",
        "country": "",
        "lang": "en"
    })
    assert resp_en.status_code == 400
    assert resp_en.get_json()["message"] == "Please fill all fields."

    resp_hi = client.post("/weather", json={
        "city": "",
        "state": "",
        "country": "",
        "lang": "hi"
    })
    assert resp_hi.status_code == 400
    assert resp_hi.get_json()["message"] == "कृपया सभी फ़ील्ड भरें।"

@patch('requests.get')
def test_weather_endpoint_alerts_translation(mock_get, client):
    """Test that calculated climate alerts are translated correctly in /weather payload"""
    # Mock geocoding and weather responses to trigger high flood risk
    mock_geo = [{
        "name": "Mumbai",
        "lat": 19.0760,
        "lon": 72.8777,
        "country": "IN",
        "state": "Maharashtra"
    }]
    
    mock_weather = {
        "main": {
            "temp": 28.5,
            "humidity": 95
        },
        "wind": {
            "speed": 15.0
        },
        "rain": {
            "1h": 80.0
        }
    }
    
    mock_forecast = {
        "list": [
            {
                "dt_txt": "2026-06-12 12:00:00",
                "main": {
                    "temp": 28.5,
                    "humidity": 95
                },
                "wind": {
                    "speed": 15.0
                },
                "rain": {
                    "3h": 80.0
                }
            }
        ] * 40
    }
    
    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self.json_data = json_data
            self.status_code = status_code
        def json(self):
            return self.json_data
        def raise_for_status(self):
            pass

    def side_effect(url, params=None, timeout=None):
        if "geo/1.0/direct" in url:
            return MockResponse(mock_geo)
        elif "data/2.5/weather" in url:
            return MockResponse(mock_weather)
        elif "data/2.5/forecast" in url:
            return MockResponse(mock_forecast)
        return MockResponse({}, 404)

    mock_get.side_effect = side_effect

    # Set weather api key to mock existence
    with patch.dict('os.environ', {'OPENWEATHER_API_KEY': 'mock_key'}):
        # 1. English Alert
        resp_en = client.post("/weather", json={
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "lang": "en"
        })
        assert resp_en.status_code == 200
        data_en = resp_en.get_json()
        assert "⚠ High Flood Risk Detected" in data_en["alerts"]

        # 2. Hindi Alert
        resp_hi = client.post("/weather", json={
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "lang": "hi"
        })
        assert resp_hi.status_code == 200
        data_hi = resp_hi.get_json()
        assert "⚠ उच्च बाढ़ जोखिम का पता चला" in data_hi["alerts"]

        # 3. Spanish Alert
        resp_es = client.post("/weather", json={
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "lang": "es"
        })
        assert resp_es.status_code == 200
        data_es = resp_es.get_json()
        assert "⚠ Riesgo de inundación alto detectado" in data_es["alerts"]

        # 4. French Alert
        resp_fr = client.post("/weather", json={
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "lang": "fr"
        })
        assert resp_fr.status_code == 200
        data_fr = resp_fr.get_json()
        assert "⚠ Risque d'inondation élevé détecté" in data_fr["alerts"]
