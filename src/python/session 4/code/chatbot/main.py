"""Main entry point for the chatbot package."""

try:
    from .chat import Chatbot
except ImportError:
    from chat import Chatbot

if __name__ == "__main__":
    Chatbot()
