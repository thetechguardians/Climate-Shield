import random
import time
import argparse

from flask import Flask, jsonify, request
from flask_cors import CORS

# ==========================================
# CLIMATE SHIELD AI CHATBOT
# ==========================================

BOT_NAME = "ClimateBot"

conversation_memory = []

# ==========================================
# KNOWLEDGE BASE
# ==========================================

knowledge = {

    "flood": {

        "what": [

            "Floods occur when excessive water submerges normally dry land.",

            "Floods are usually caused by heavy rainfall, overflowing rivers, or poor drainage systems."
        ],

        "precautions": [

            "You should avoid low-lying areas during floods.",

            "Keep emergency supplies and important documents ready.",

            "Move to higher ground if flood warnings are issued."
        ],

        "effects": [

            "Floods can damage homes, roads, agriculture, and power systems.",

            "Severe floods may also contaminate drinking water sources."
        ]
    },

    "heatwave": {

        "what": [

            "A heatwave is a prolonged period of extremely high temperature.",

            "Heatwaves are becoming more frequent due to climate change."
        ],

        "precautions": [

            "Drink plenty of water and avoid direct sunlight.",

            "Stay indoors during peak afternoon temperatures.",

            "Wear light-colored clothing during extreme heat."
        ]
    },

    "cyclone": {

        "what": [

            "Cyclones are intense storms formed over warm ocean waters.",

            "Cyclones can produce strong winds, flooding, and heavy rainfall."
        ],

        "precautions": [

            "Stay indoors and follow evacuation warnings.",

            "Keep batteries, food, and emergency kits ready."
        ]
    },

    "climate change": {
        "what": [
            "Climate change refers to long-term changes in Earth's climate patterns.",
            "Global warming is increasing the intensity of extreme weather events."
        ],
        "effects": [
            "Climate change affects rainfall, sea levels, agriculture, and ecosystems.",
            "It also increases risks of floods, droughts, and heatwaves."
        ]
    },
    "wildfire": {
        "what": [
            "Wildfires are unplanned, unwanted fires burning in a natural area.",
            "Wildfires are fueled by dry vegetation, high temperatures, and strong winds."
        ],
        "precautions": [
            "Stay indoors with windows closed to keep out smoke.",
            "Prepare an emergency supply kit and plan evacuation routes.",
            "Follow instructions from local emergency authorities."
        ],
        "effects": [
            "Wildfires destroy forests, habitats, homes, and affect air quality.",
            "They can also cause respiratory health issues due to smoke."
        ]
    },
    "drought": {
        "what": [
            "A drought is a prolonged period of dry weather due to a lack of rainfall.",
            "Droughts are slow-onset hazards that develop over months or years."
        ],
        "precautions": [
            "Practice water conservation and fix leaks immediately.",
            "Avoid washing vehicles or watering lawns during dry periods.",
            "Follow municipal water usage restrictions."
        ],
        "effects": [
            "Droughts impact agriculture, dry up water sources, and increase wildfire risk.",
            "They can lead to food shortages and damage ecosystems."
        ]
    }
}

# ==========================================
# HUMAN-LIKE FILLERS
# ==========================================

starters = [

    "That's an important question.",
    "Interesting topic.",
    "Here's what I know.",
    "Let me explain.",
    "Sure."
]

followups = [

    "Would you like to know more?",
    "I can also explain precautions if you'd like.",
    "Climate awareness is very important.",
    "These events are becoming more common globally."
]

# ==========================================
# TYPING EFFECT
# ==========================================

def type_text(text):

    for char in text:

        print(char, end="", flush=True)

        time.sleep(0.015)

    print()

# ==========================================
# DETECT TOPIC
# ==========================================

def detect_topic(user):

    user = user.lower()

    if "flood" in user:
        return "flood"

    elif "heat" in user:
        return "heatwave"

    elif "cyclone" in user or "storm" in user:
        return "cyclone"

    elif "wildfire" in user or "fire" in user:
        return "wildfire"

    elif "drought" in user or "dry" in user:
        return "drought"

    elif "climate" in user or "global warming" in user:
        return "climate change"

    return None

# ==========================================
# DETECT QUESTION TYPE
# ==========================================

def detect_question_type(user):

    user = user.lower()

    if any(word in user for word in
           ["what", "define", "explain"]):

        return "what"

    elif any(word in user for word in
             ["precaution", "prevent", "safety", "protect"]):

        return "precautions"

    elif any(word in user for word in
             ["effect", "impact", "damage"]):

        return "effects"

    return "what"

# ==========================================
# AI RESPONSE ENGINE
# ==========================================

def generate_response(user_input, context_summary=""):

    full_input = (context_summary + " User asked: " + user_input).strip()
    user = full_input.lower()

    conversation_memory.append(user)

    # ======================================
    # BASIC CONVERSATION
    # ======================================

    if any(word in user for word in
           ["hello", "hi", "hey"]):

        return random.choice([

            "Hello 👋 I'm ClimateBot.",
            "Hi. How can I help you today?",
            "Greetings from Climate Shield 🌍"
        ])

    if "how are you" in user:

        return random.choice([

            "I'm functioning perfectly 🌍",
            "Doing great and monitoring climate conditions.",
            "All systems operational."
        ])

    if any(word in user for word in
           ["thank", "thanks"]):

        return random.choice([

            "You're welcome 🌍",
            "Glad I could help.",
            "Stay safe."
        ])

    # ======================================
    # CONTEXT MEMORY
    # ======================================

    if "what should i do" in user:

        previous_topics = " ".join(
            conversation_memory[-5:]
        )

        if "flood" in previous_topics:

            return random.choice(
                knowledge["flood"]["precautions"]
            )

        elif "heatwave" in previous_topics:

            return random.choice(
                knowledge["heatwave"]["precautions"]
            )

        elif "cyclone" in previous_topics:

            return random.choice(
                knowledge["cyclone"]["precautions"]
            )

        elif "wildfire" in previous_topics:

            return random.choice(
                knowledge["wildfire"]["precautions"]
            )

        elif "drought" in previous_topics:

            return random.choice(
                knowledge["drought"]["precautions"]
            )

    # ======================================
    # TOPIC DETECTION
    # ======================================

    topic = detect_topic(user)

    if topic:

        qtype = detect_question_type(user)

        if qtype in knowledge[topic]:

            response = (
                random.choice(starters)
                + " "
                + random.choice(
                    knowledge[topic][qtype]
                )
            )

            if random.random() > 0.5:

                response += (
                    " " +
                    random.choice(followups)
                )

            return response

    # ======================================
    # GENERAL AI-LIKE RESPONSES
    # ======================================

    smart_responses = [

        "Could you explain that differently?",

        "Could you be more specific?",

        "I understand partially. Can you elaborate?",

        "That topic seems outside my current scope. I can best assist you with queries related to climate systems",

        "I am afraid I can't help you with this topic, but I would love to answer your questions related to climate hazards.",

        "Please select from one of the above mentioned topics.",

        "Try asking me a question from these topics- flood, cyclone, wildfire, heatwave." 
    ]

    return random.choice(smart_responses)

# ==========================================
# MAIN LOOP
# ==========================================

def main():

    print("\n====================================")
    print("        CLIMATE SHIELD AI")
    print("====================================")

    print("\nType 'exit' to close chatbot.\n")

    while True:

        user_input = input("You : ")

        if user_input.lower() in [
            "exit",
            "quit",
            "bye"
        ]:

            print()

            type_text(
                f"{BOT_NAME} : Goodbye 🌍 Stay safe."
            )

            break

        print()

        response = generate_response(
            user_input
        )

        type_text(
            f"{BOT_NAME} : {response}"
        )

        print()

# ==========================================
# CONTEXT-AWARE RISK DESCRIPTIONS
# ==========================================

def descriptions_for_bot(risk_type, score):
    messages = {
        'flood':    {
            'low':      'No significant flood risk. Normal conditions.',
            'moderate': 'Some flood potential. Avoid low-lying areas during heavy rain.',
            'high':     'Elevated flood risk. Stay away from rivers and flood-prone zones.',
            'critical': 'Dangerous flood conditions. Move to higher ground immediately.',
        },
        'heat':     {
            'low':      'Heat levels are comfortable.',
            'moderate': 'Mild heat stress possible. Stay hydrated.',
            'high':     'High heat risk. Avoid outdoor exertion.',
            'critical': 'Extreme heat emergency. Stay indoors.',
        },
        'drought':  {
            'low':      'Water supply is normal.',
            'moderate': 'Some drought stress. Consider conserving water.',
            'high':     'Significant drought. Restrict non-essential water use.',
            'critical': 'Severe drought. Comply with all rationing measures.',
        },
        'wildfire': {
            'low':      'No fire risk.',
            'moderate': 'Some fire risk. Avoid open burning.',
            'high':     'Elevated wildfire risk. Do not light outdoor fires.',
            'critical': 'Critical fire danger. Follow evacuation orders immediately.',
        },
        'cyclone':  {
            'low':      'No cyclone activity expected.',
            'moderate': 'Low-level cyclone indicators. Monitor weather bulletins.',
            'high':     'Significant cyclone risk. Secure your home and plan evacuation.',
            'critical': 'Severe cyclone warning. Seek sturdy shelter immediately.',
        },
    }
    if score <= 0.29:   key = 'low'
    elif score <= 0.49: key = 'moderate'
    elif score <= 0.69: key = 'high'
    else:               key = 'critical'
    return messages.get(risk_type, {}).get(key, '')


# ==========================================
# API SERVER
# ==========================================

app = Flask(__name__)
CORS(app)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "success": True,
        "bot": BOT_NAME
    })


def handle_chatbot_request(data):
    data = data or {}
    user_message = str(data.get("message", "")).strip()
    context = data.get('context')  # will be None if no analysis has been run yet

    context_summary = ""
    loc = {}
    risks = {}

    if context:
        loc   = context.get('location', {})
        risks = context.get('risks', {})
        wx    = context.get('weather', {})

        def fmt(val):
            return f"{float(val):.3f}" if val is not None else "N/A"

        def level(val):
            if val is None: return "Unknown"
            v = float(val)
            if v <= 0.29: return "Low"
            if v <= 0.49: return "Moderate"
            if v <= 0.69: return "High"
            return "Critical"

        context_summary = (
            f"The user has just analysed {loc.get('city','')}, "
            f"{loc.get('state','')}, {loc.get('country','')}. "
            f"Current weather: {wx.get('temperature','N/A')}°C temperature, "
            f"{wx.get('humidity','N/A')}% humidity, "
            f"{wx.get('rainfall','N/A')} mm rainfall, "
            f"{wx.get('wind_speed','N/A')} km/h wind. "
            f"Risk scores — "
            f"Flood: {fmt(risks.get('flood_risk'))} ({level(risks.get('flood_risk'))}), "
            f"Heat: {fmt(risks.get('heat_risk'))} ({level(risks.get('heat_risk'))}), "
            f"Wildfire: {fmt(risks.get('wildfire_risk'))} ({level(risks.get('wildfire_risk'))}), "
            f"Cyclone: {fmt(risks.get('cyclone_risk'))} ({level(risks.get('cyclone_risk'))}), "
            f"Drought: {fmt(risks.get('drought_risk'))} ({level(risks.get('drought_risk'))})."
        )

    if not user_message:
        return {
            "success": False,
            "message": "Please provide a message."
        }, 400

    msg_lower = user_message.lower()
    response = None

    if context_summary and any(phrase in msg_lower for phrase in [
        'am i safe', 'is it safe', 'should i be worried',
        'what should i do', 'my risk', 'current risk',
        'how bad', 'is it dangerous', 'tell me about my'
    ]):
        highest_risk = max(
            [('Flood',    risks.get('flood_risk',    0)),
             ('Heat',     risks.get('heat_risk',     0)),
             ('Wildfire', risks.get('wildfire_risk', 0)),
             ('Cyclone',  risks.get('cyclone_risk',  0)),
             ('Drought',  risks.get('drought_risk',  0))],
            key=lambda x: x[1]
        )
        response = (
            f"Based on your analysis for {loc.get('city','your location')}: "
            f"your highest current risk is {highest_risk[0]} "
            f"({highest_risk[1]:.3f} — {level(highest_risk[1])}). "
            f"{context_summary.split('Risk scores')[0].strip()} "
            f"Monitor local advisories and refer to the risk cards for full details."
        )

    elif context_summary and any(phrase in msg_lower for phrase in [
        'flood risk', 'flood score'
    ]):
        response = (
            f"Your Flood Risk for {loc.get('city','')} is "
            f"{fmt(risks.get('flood_risk'))} — {level(risks.get('flood_risk'))}. "
            + descriptions_for_bot('flood', risks.get('flood_risk', 0))
        )

    if response is None:
        response = generate_response(user_message, context_summary)

    return {
        "success": True,
        "response": response
    }, 200


@app.route("/chatbot", methods=["POST"])
def chatbot_reply():
    data = request.get_json(silent=True) or {}
    payload, status = handle_chatbot_request(data)
    return jsonify(payload), status


def run_api_server(host="127.0.0.1", port=5001):
    app.run(host=host, port=port, debug=True)


# ==========================================
# RUN CHATBOT
# ==========================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Climate Shield chatbot runner"
    )
    parser.add_argument(
        "--mode",
        choices=["api", "cli"],
        default="api",
        help="Run chatbot as API server or CLI."
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="API host (only used in api mode)."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5001,
        help="API port (only used in api mode)."
    )

    args = parser.parse_args()

    if args.mode == "cli":
        main()
    else:
        run_api_server(args.host, args.port)
