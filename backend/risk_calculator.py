def calculate_risk_scores(temp_val, humid_val, wind_val, rain_val):
    flood_risk_metric = round(min(1.0, (rain_val * 0.6 + humid_val * 0.3 + wind_val * 0.1) / 100), 3)
    heat_risk_metric = round(min(1.0, (max(temp_val - 25, 0) * 2 + humid_val * 0.3) / 100), 3)
    wildfire_risk_metric = round(min(1.0, (max(temp_val - 32, 0) * 1.5 + (100 - humid_val) * 0.5 + wind_val * 0.2) / 100), 3)
    cyclone_risk_metric = round(min(1.0, (wind_val * 1.5 + rain_val * 0.5) / 100), 3)
    drought_risk_metric = round(min(1.0, (max(temp_val - 28, 0) + (100 - humid_val)) / 100), 3)

    return {
        "flood_risk": flood_risk_metric,
        "heat_risk": heat_risk_metric,
        "wildfire_risk": wildfire_risk_metric,
        "cyclone_risk": cyclone_risk_metric,
        "drought_risk": drought_risk_metric,
    }

def get_risk_level(metric):
    if metric >= 0.6:
        return "HIGH"
    elif metric >= 0.3:
        return "MEDIUM"
    return "LOW"

def get_detailed_risks(scores):
    details = {}
    for risk_type, metric in scores.items():
        details[risk_type] = metric
        details[f"{risk_type}_confidence"] = round(metric * 100, 1)
        details[f"{risk_type}_level"] = get_risk_level(metric)
    return details

def generate_alerts(scores):
    alerts = []
    if scores["flood_risk"] >= 0.6:
        alerts.append("⚠ High Flood Risk Detected")
    if scores["heat_risk"] >= 0.6:
        alerts.append("🔥 Heatwave Conditions Possible")
    if scores["wildfire_risk"] >= 0.6:
        alerts.append("🌲 Elevated Wildfire Risk")
    if scores["cyclone_risk"] >= 0.6:
        alerts.append("🌀 Cyclone Risk Detected")
    if scores["drought_risk"] >= 0.6:
        alerts.append("☀ Drought Conditions Possible")
        
    if not alerts:
        alerts.append("✅ No major climate threats detected.")
    return alerts
