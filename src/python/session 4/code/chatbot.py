"""Simple rule-based chatbot implementation."""

import random

# Predefined responses
responses = {
    "hello": [
        "Hello!",
        "Hi there!",
        "Greetings!"
    ],
    "how are you": [
        "I'm doing well, thank you!",
        "I'm fine, how about you?"
    ],
    "goodbye": [
        "Goodbye!",
        "See you later!",
        "Farewell!"
    ],
    "default": [
        "I'm sorry, I didn't understand.",
        "Could you please rephrase that?"
    ]
}


def get_response(user_input):
    """Return a chatbot response matching the user input."""
    for key, value in responses.items():
        if key in user_input:
            return random.choice(value)

    return random.choice(responses["default"])


# Chatbot function
def chatbot():
    """Run the chatbot interaction loop."""
    print("Chatbot: Hi! How can I assist you today?")

    while True:
        user_input = input("User: ").lower()
        response = get_response(user_input)
        print("Chatbot:", response)

        if user_input == "goodbye":
            break


# Run the chatbot
chatbot()
