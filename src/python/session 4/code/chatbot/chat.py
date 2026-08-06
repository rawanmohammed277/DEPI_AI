"""Simple chatbot application entry point."""

from response import get_response


def chatbot():
    """Start the chatbot loop and handle user input."""
    print("Chatbot: Hi! How can I assist you today?")

    while True:
        user_input = input("User: ").lower()
        response = get_response(user_input)
        print("Chatbot:", response)

        if user_input == "goodbye":
            break


# Run the chatbot

if __name__ == "__main__":
    chatbot()
