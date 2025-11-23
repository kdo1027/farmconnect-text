"""
Test script for FarmConnect chatbot
Run this to test the bot logic locally without WhatsApp

Usage: python tests/test_bot_integration.py
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot import FarmConnectBot

def test_conversation():
    """Test a conversation flow"""
    bot = FarmConnectBot()

    print("=" * 50)
    print("FarmConnect Bot Test")
    print("=" * 50)
    print()

    # Simulate a farmer registration
    test_phone = "whatsapp:+15555551234"

    print("Test 1: Welcome Message")
    response = bot.handle_message(test_phone, "Hi")
    print(f"Bot: {response}\n")

    print("Test 2: Select Farmer Role")
    response = bot.handle_message(test_phone, "1")
    print(f"Bot: {response}\n")

    print("Test 3: Enter Name")
    response = bot.handle_message(test_phone, "John Doe")
    print(f"Bot: {response}\n")

    print("Test 4: Enter Location")
    response = bot.handle_message(test_phone, "Sacramento, CA")
    print(f"Bot: {response}\n")

    print("Test 5: Simulate ID Upload (with media URL)")
    response = bot.handle_message(test_phone, "Here's my ID", "https://example.com/id.jpg")
    print(f"Bot: {response}\n")

    print("Test 6: Work Type Preference")
    response = bot.handle_message(test_phone, "Harvesting, Planting")
    print(f"Bot: {response}\n")

    print("Test 7: Pay Rate")
    response = bot.handle_message(test_phone, "15")
    print(f"Bot: {response}\n")

    print("Test 8: Max Distance")
    response = bot.handle_message(test_phone, "25")
    print(f"Bot: {response}\n")

    print("Test 9: Hours Preference")
    response = bot.handle_message(test_phone, "1")
    print(f"Bot: {response}\n")

    # Check user data
    user = bot.store.get_user(test_phone)
    print("=" * 50)
    print("User Profile:")
    print(f"Type: {user['type']}")
    print(f"Registered: {user['registered']}")
    print(f"Profile: {user['profile']}")
    print("=" * 50)

if __name__ == "__main__":
    test_conversation()
    print("\nTest completed! Check the 'data/' directory for JSON files.")
