import pytest
from backend.risk_calculator import calculate_risk_scores, get_risk_level, get_detailed_risks, generate_alerts

def test_calculate_risk_scores_normal():
    # Moderate temperature, normal humidity, low wind, no rain
    scores = calculate_risk_scores(temp_val=25, humid_val=50, wind_val=10, rain_val=0)
    
    assert 0 <= scores["flood_risk"] <= 1.0
    assert 0 <= scores["heat_risk"] <= 1.0
    assert 0 <= scores["wildfire_risk"] <= 1.0
    assert 0 <= scores["cyclone_risk"] <= 1.0
    assert 0 <= scores["drought_risk"] <= 1.0
    
    # Check specific values based on formula
    # heat_risk = max(25-25,0)*2 + 50*0.3 / 100 = 15/100 = 0.15
    assert scores["heat_risk"] == 0.15

def test_calculate_risk_scores_extreme_heat():
    # High temp, low humidity
    scores = calculate_risk_scores(temp_val=45, humid_val=10, wind_val=5, rain_val=0)
    
    # heat_risk = (max(45-25,0)*2 + 10*0.3)/100 = (40 + 3)/100 = 0.43
    assert scores["heat_risk"] == 0.43
    
    # wildfire_risk = (max(45-32)*1.5 + 90*0.5 + 5*0.2)/100 = (19.5 + 45 + 1)/100 = 0.655
    assert scores["wildfire_risk"] == 0.655

def test_calculate_risk_scores_extreme_flood():
    # Heavy rain, high wind
    scores = calculate_risk_scores(temp_val=20, humid_val=95, wind_val=50, rain_val=150)
    
    # flood = (150*0.6 + 95*0.3 + 50*0.1)/100 = (90 + 28.5 + 5)/100 = 1.235 -> capped at 1.0
    assert scores["flood_risk"] == 1.0
    
    # cyclone = (50*1.5 + 150*0.5)/100 = (75 + 75)/100 = 1.5 -> capped at 1.0
    assert scores["cyclone_risk"] == 1.0

def test_calculate_risk_scores_extreme_drought():
    # Very high temp, extremely low humidity, zero rain
    scores = calculate_risk_scores(temp_val=40, humid_val=5, wind_val=20, rain_val=0)
    
    # drought = (max(40-28, 0) + (100 - 5)) / 100 = (12 + 95)/100 = 1.07 -> capped at 1.0
    assert scores["drought_risk"] == 1.0

def test_calculate_risk_scores_extreme_cold():
    # Cold temperatures should yield 0 for heat and wildfire risk contribution from temp
    scores = calculate_risk_scores(temp_val=-10, humid_val=80, wind_val=15, rain_val=0)
    
    assert scores["heat_risk"] == 0.24 # (max(-10-25, 0)*2 + 80*0.3)/100 = (0 + 24)/100 = 0.24
    assert scores["wildfire_risk"] == 0.13 # (max(-10-32, 0)*1.5 + 20*0.5 + 15*0.2)/100 = (0 + 10 + 3)/100 = 0.13
    assert scores["drought_risk"] == 0.2 # (max(-10-28, 0) + 20)/100 = 0.2

def test_get_risk_level():
    assert get_risk_level(0.1) == "LOW"
    assert get_risk_level(0.3) == "MEDIUM"
    assert get_risk_level(0.59) == "MEDIUM"
    assert get_risk_level(0.6) == "HIGH"
    assert get_risk_level(1.0) == "HIGH"

def test_get_detailed_risks():
    scores = {"flood_risk": 0.65, "heat_risk": 0.2}
    detailed = get_detailed_risks(scores)
    
    assert detailed["flood_risk"] == 0.65
    assert detailed["flood_risk_confidence"] == 65.0
    assert detailed["flood_risk_level"] == "HIGH"
    
    assert detailed["heat_risk"] == 0.2
    assert detailed["heat_risk_confidence"] == 20.0
    assert detailed["heat_risk_level"] == "LOW"

def test_generate_alerts():
    # High risk
    high_risk_scores = {
        "flood_risk": 0.8,
        "heat_risk": 0.2,
        "wildfire_risk": 0.1,
        "cyclone_risk": 0.9,
        "drought_risk": 0.0
    }
    alerts = generate_alerts(high_risk_scores)
    assert len(alerts) == 2
    assert "⚠ High Flood Risk Detected" in alerts
    assert "🌀 Cyclone Risk Detected" in alerts

    # Low risk
    low_risk_scores = {
        "flood_risk": 0.1,
        "heat_risk": 0.1,
        "wildfire_risk": 0.1,
        "cyclone_risk": 0.1,
        "drought_risk": 0.1
    }
    alerts_low = generate_alerts(low_risk_scores)
    assert len(alerts_low) == 1
    assert "✅ No major climate threats detected." in alerts_low
