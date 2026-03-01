import wikipedia

ALLOWED_TOPICS = [
    "flood",
    "flooding",
    "heat wave",
    "heatwave",
    "heat stroke",
    "monsoon",
    "climate change"
]

def is_valid_topic(user_input):
    user_input = user_input.lower()
    return any(topic in user_input for topic in ALLOWED_TOPICS)

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    if not is_valid_topic(user_input):
        print("Bot: I only provide information about floods and heat waves.")
        continue

    try:
        summary = wikipedia.summary(user_input, sentences=3)
        print("Bot:", summary)

    except wikipedia.exceptions.DisambiguationError as e:
        print("Bot: Be more specific. Possible options:", e.options[:5])

    except wikipedia.exceptions.PageError:
        print("Bot: I couldn't find information on that topic.")

    except Exception as e:
        print("Error:", e)