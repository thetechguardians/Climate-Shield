import json
import os
from deep_translator import GoogleTranslator

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

en_data = {
    "nav_features": "Features",
    "nav_analyze": "Analyze",
    "nav_contact": "Contact",
    "nav_github": "GitHub",
    "nav_start_analysis": "Start Analysis",
    "brand_subtitle": "Climate intelligence, instantly",
    "hero_eyebrow": "Real-time weather risk monitoring",
    "hero_title": "Predict climate threats before they interrupt your day.",
    "hero_desc": "Climate Shield combines live weather signals with fast risk scoring to highlight flood and heatwave exposure in seconds.",
    "hero_analyze_btn": "Analyze a location",
    "hero_insights_btn": "View insights",
    "stat_live": "live monitoring",
    "stat_risk": "risk types tracked",
    "stat_alert": "alert delivery",
    "step_heading1": "3 steps to climate resilience",
    "step_heading2": "Build stronger readiness with climate-smart actions.",
    "step1_title": "Step 1",
    "step1_desc": "Open the analysis page",
    "step2_title": "Step 2",
    "step2_desc": "Enter city, state, and country",
    "step3_title": "Step 3",
    "step3_desc": "Review weather, risk, and alerts",
    "feat_heading1": "Why it helps",
    "feat_heading2": "Built for quick decisions when weather conditions change.",
    "feat1_title": "Live weather context",
    "feat1_desc": "See current temperature, humidity, rainfall, and wind in one clean snapshot.",
    "feat2_title": "Risk-first summary",
    "feat2_desc": "Flood and heat risks are presented as clear signals, not just raw numbers.",
    "feat3_title": "Actionable alerts",
    "feat3_desc": "Important warnings are surfaced immediately so users can react faster.",
    "cap_heading1": "Platform Capabilities",
    "cap_heading2": "Powerful climate intelligence for proactive decision-making.",
    "cap1_title": "Climate Risk Prediction",
    "cap1_desc": "Predict potential climate threats using weather patterns and risk scoring models.",
    "cap2_title": "Flood & Heatwave Analysis",
    "cap2_desc": "Evaluate flood and heatwave risks with easy-to-understand climate indicators.",
    "cap3_title": "AI-Powered Climate Assistant",
    "cap3_desc": "Get instant answers and climate safety guidance through ClimateBot.",
    "cap4_title": "Location-Based Insights",
    "cap4_desc": "Analyze climate conditions for specific cities and regions worldwide.",
    "cap5_title": "Environmental Intelligence",
    "cap5_desc": "Access real-time environmental information to support informed decisions.",
    "chatbot_title": "ClimateBot Assistant",
    "chatbot_desc": "Ask about floods, heatwaves, cyclones, and climate change.",
    "chatbot_placeholder": "Type your question...",
    "chatbot_send": "Send",
    "analysis_search_title": "Analyze Location Risk",
    "analysis_search_desc": "Enter a location to receive instant risk scores for flood, heatwave, and other climate hazards.",
    "analysis_city": "City",
    "analysis_state": "State",
    "analysis_country": "Country",
    "analysis_btn": "Analyze Risks",
    "analysis_loading": "Loading...",
    "analysis_summary_title": "Climate Risk Summary",
    "analysis_risk_score": "Risk Score",
    "analysis_temperature": "Temperature",
    "analysis_humidity": "Humidity",
    "analysis_rainfall": "Rainfall",
    "analysis_wind": "Wind",
    "analysis_alerts_title": "Active Alerts",
    "analysis_forecast_title": "Forecast"
}

def translate_dict(d, target_lang):
    print(f"Translating to {target_lang}...")
    translator = GoogleTranslator(source='en', target=target_lang)
    translated_d = {}
    for k, v in d.items():
        translated_d[k] = translator.translate(v)
    return translated_d

os.makedirs('Frontend/locales/en', exist_ok=True)
with open('Frontend/locales/en/translation.json', 'w', encoding='utf-8') as f:
    json.dump(en_data, f, ensure_ascii=False, indent=2)

for lang_code, lang_name in langs.items():
    os.makedirs(f'Frontend/locales/{lang_code}', exist_ok=True)
    out_path = f'Frontend/locales/{lang_code}/translation.json'
    if not os.path.exists(out_path):
        td = translate_dict(en_data, lang_code)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(td, f, ensure_ascii=False, indent=2)
    else:
        print(f"Skipping {lang_code}, already exists.")

print("Done translating frontend.")
