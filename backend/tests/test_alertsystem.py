# tests/test_alertsystem.py
import pytest
from backend.alertsystem import calculate_flood_risk, calculate_heatwave_risk

def test_flood_risk_normal_case():
    assert 0 <= calculate_flood_risk(100, 5) <= 1
    assert pytest.approx(calculate_flood_risk(200, 10), 0.01) == 1.0

def test_flood_risk_edge_cases():
    assert calculate_flood_risk(0, 0) == 0.0
    assert calculate_flood_risk(-50, -2) == 0.0  # negative inputs clamp to 0
    assert calculate_flood_risk(500, 20) == 1.0  # extreme inputs clamp to 1

def test_heatwave_risk_normal_case():
    score = calculate_heatwave_risk(40, 50)
    assert 0 <= score <= 1
    assert pytest.approx(score, 0.01) == 0.55  # expected mid‑range

def test_heatwave_risk_edge_cases():
    assert calculate_heatwave_risk(30, 100) == 0.0  # cool + humid
    assert calculate_heatwave_risk(50, 0) == 1.0   # extreme hot + dry
    assert calculate_heatwave_risk(25, 80) == 0.0  # below threshold temp
