import pytest
import json

def test_chatbot_api_missing_message(client):
    response = client.post("/chatbot", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "Please provide a message" in data["message"]

def test_chatbot_api_greeting(client):
    response = client.post("/chatbot", json={"message": "hello"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "response" in data
    assert any(phrase in data["response"] for phrase in ["Hello", "Hi", "Greetings"])

def test_chatbot_api_knowledge_base(client):
    response = client.post("/chatbot", json={"message": "what is a flood?"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "flood" in data["response"].lower() or "submerge" in data["response"].lower()

def test_chatbot_api_with_context(client):
    payload = {
        "message": "is it safe?",
        "context": {
            "location": {"city": "Mumbai", "state": "MH", "country": "IN"},
            "weather": {"temperature": 32, "humidity": 85, "rainfall": 120, "wind_speed": 15},
            "risks": {
                "flood_risk": 0.85,
                "heat_risk": 0.2,
                "wildfire_risk": 0.05,
                "cyclone_risk": 0.3,
                "drought_risk": 0.1
            }
        }
    }
    response = client.post("/chatbot", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    # The chatbot should mention the highest risk (Flood) based on context
    assert "Flood" in data["response"]
    assert "0.850" in data["response"]

def test_chatbot_api_unknown_topic(client):
    response = client.post("/chatbot", json={"message": "how do I cook pasta?"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    # The chatbot should gracefully handle unknown topic
    assert isinstance(data["response"], str) and len(data["response"]) > 0

def test_chatbot_api_empty_payload(client):
    response = client.post("/chatbot", data="")
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
