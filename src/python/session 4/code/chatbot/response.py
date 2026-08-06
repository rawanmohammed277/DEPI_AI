"""Simple chatbot response module."""

import random

# Predefined responses
responses = {
    "hello": ["Hello!", "Hi there!", "Greetings!"],
    "how are you": [
        "I'm doing well, thank you!",
        "I'm fine, how about you?"
    ],
    "goodbye": ["Goodbye!", "See you later!", "Farewell!"],
    "default": [
        "I'm sorry, I didn't understand.",
        "Could you please rephrase that?"
    ]
}


# Function to get a response based on user input
def get_response(user_input):
    """
    Get a response based on user input.
    Args:
        user_input (str): The user's input message
    Returns:
        str: A random response from the predefined responses dictionary.
    """
    for key, value in responses.items():
        if key in user_input:
            return random.choice(value)
    return random.choice(responses["default"])
