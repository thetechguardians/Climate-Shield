import json
import os
from deep_translator import GoogleTranslator

new_en_strings = {
    "nav_analyze_now": "Analyze now",
    "analysis_hero_eyebrow": "Weather analysis workspace",
    "analysis_hero_h1": "Check flood and heat risk for any location in seconds.",
    "analysis_hero_p": "Enter a city, state, and country to pull live weather data, summarize risk, and surface alerts in a clean, readable format.",
    "stat_live_strong": "Live",
    "stat_weather_fetch": "Weather fetch",
    "stat_fast_strong": "Fast",
    "stat_risk_scoring": "Risk scoring",
    "stat_clear_strong": "Clear",
    "stat_alert_feedback": "Alert feedback",
    "analysis_workflow_lbl": "Analysis workflow",
    "analysis_workflow_h2": "One focused workspace for live weather, risk summaries, and alerts.",
    "analysis_workflow_p": "Use the form below to generate the report. The results panel appears beneath it so the flow reads like a clean report.",
    "meta_live_fetch": "Live fetch",
    "meta_weather_res": "Backend weather response",
    "meta_risk_view": "Risk view",
    "meta_signals": "Flood and heat signals",
    "meta_alerts": "Alerts",
    "meta_clear_output": "Clear output for action",
    "analysis_use_loc": "Use Current Location",
    "analysis_clear_all": "🗑 Clear All",
    "analysis_recent_searches": "Recent Searches ▼",
    "analysis_clear_history": "🗑 Clear History",
    "analysis_complete_kicker": "Analysis complete",
    "analysis_ready_review": "Ready to review location risk",
    "analysis_waiting_input": "Waiting for input",
    "analysis_loc_under": "📌 Location Under Analysis",
    "analysis_demo_mode": "⚠️ Demo Mode Active: Serving simulated weather parameters.",
    "analysis_live_weather_report": "📍 Live Weather Report",
    "analysis_risk_analysis": "⚠ Climate Risk Analysis",
    "analysis_map": "🗺 Interactive GIS Climate Map",
    "analysis_recommendations": "🛡 Safety Recommendations",
    "analysis_forecast_desc": "Forecast metrics modeled at 12:00 PM daily. Hover over values to inspect trends.",
    "analysis_forecast_temp": "📈 Temperature & Rainfall Forecast",
    "analysis_forecast_risk": "🛡 Daily Climate Risk Index Trends",
    "analysis_subscribe_warnings": "🔔 Subscribe to Local Warnings",
    "analysis_subscribe_desc": "Register your email to receive simulated notification dispatches when local risk levels exceed safety thresholds.",
    "analysis_opt_all": "All Warnings",
    "analysis_opt_flood": "Flooding Only",
    "analysis_opt_heat": "Extreme Heat Only",
    "analysis_opt_wildfire": "Wildfire Danger Only",
    "analysis_activate_alert": "Activate Alert Stream",
    "analysis_sub_active": "✓ Subscription active! Emergency dispatches will be routed to the live logs.",
    "analysis_dispatch_title": "🛡 Climate Shield Emergency Dispatch",
    "analysis_dispatch_desc": "Live alert logs processed for this region:",
    "analysis_log1": "Monitoring node activated. No active hazards detected.",
    "analysis_log2": "Moisture deficit elevated. Local crop warning active.",
    "analysis_log3": "Flood threshold exceeded. Immediate action required.",
    "widget_weather_status": "Weather Status",
    "widget_flood_risk": "Flood Risk Gauge",
    "widget_regional_alert": "REGIONAL EXPOSURE ALERT",
    "analysis_flood_risk": "Flood Risk",
    "analysis_heat_risk": "Heat Risk",
    "analysis_wildfire_risk": "Wildfire Risk",
    "analysis_cyclone_risk": "Cyclone Risk",
    "analysis_drought_risk": "Drought Risk",
    "brand_desc_short": "Real-time weather risk monitoring for flood and heatwave awareness.",
    "brand_tagline": "Protecting communities with fast, simple climate risk visibility.",
    "footer_nav": "Navigate",
    "footer_nav_home": "Home",
    "footer_nav_features": "Features",
    "footer_nav_analysis": "Analysis",
    "footer_nav_bot": "Climate Bot",
    "footer_resources": "Resources",
    "footer_res_issue": "Report an Issue",
    "footer_res_discuss": "Discussions",
    "footer_res_contrib": "Contributing",
    "footer_res_docs": "Documentation",
    "footer_community": "Community",
    "footer_comm_contribs": "Contributors",
    "footer_comm_github": "GitHub Repository",
    "footer_comm_license": "MIT License",
    "footer_made_by": "Made with ♥ by The Tech Guardians"
}

langs = {
    'hi': 'hindi',
    'mr': 'marathi',
    'kn': 'kannada',
    'ml': 'malayalam',
    'te': 'telugu',
    'ta': 'tamil',
    'es': 'spanish',
    'fr': 'french'
}

with open('Frontend/locales/en/translation.json', 'r', encoding='utf-8') as f:
    en_data = json.load(f)

# update en_data with new keys
for k, v in new_en_strings.items():
    if k not in en_data:
        en_data[k] = v

with open('Frontend/locales/en/translation.json', 'w', encoding='utf-8') as f:
    json.dump(en_data, f, ensure_ascii=False, indent=2)

def translate_dict(d, target_lang):
    print(f"Translating {len(d)} keys to {target_lang}...")
    translator = GoogleTranslator(source='en', target=target_lang)
    translated_d = {}
    for k, v in d.items():
        translated_d[k] = translator.translate(v)
    return translated_d

for lang_code, lang_name in langs.items():
    os.makedirs(f'Frontend/locales/{lang_code}', exist_ok=True)
    out_path = f'Frontend/locales/{lang_code}/translation.json'
    
    lang_data = {}
    if os.path.exists(out_path):
        with open(out_path, 'r', encoding='utf-8') as f:
            lang_data = json.load(f)
    
    keys_to_translate = {k: v for k, v in en_data.items() if k not in lang_data}
    
    if keys_to_translate:
        try:
            new_translations = translate_dict(keys_to_translate, lang_code)
            lang_data.update(new_translations)
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(lang_data, f, ensure_ascii=False, indent=2)
            print(f"Updated {lang_code}.")
        except Exception as e:
            print(f"Error translating {lang_code}: {e}")
    else:
        print(f"Skipping {lang_code}, all keys translated.")

print("Done translating frontend.")
