#!/usr/bin/env python3
"""
Quick test script to verify Twilio SMS configuration
"""

import os
from twilio.rest import Client

# Read credentials from environment
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_FROM = os.getenv("TWILIO_PHONE_FROM")
TWILIO_PHONE_TO = os.getenv("TWILIO_PHONE_TO")

def test_sms():
    """Send a test SMS to verify Twilio configuration"""

    # Check if all credentials are set
    print("Checking configuration...")
    print(f"TWILIO_ACCOUNT_SID: {'✓ Set' if TWILIO_ACCOUNT_SID else '✗ Missing'}")
    print(f"TWILIO_AUTH_TOKEN: {'✓ Set' if TWILIO_AUTH_TOKEN else '✗ Missing'}")
    print(f"TWILIO_PHONE_FROM: {TWILIO_PHONE_FROM if TWILIO_PHONE_FROM else '✗ Missing'}")
    print(f"TWILIO_PHONE_TO: {TWILIO_PHONE_TO if TWILIO_PHONE_TO else '✗ Missing'}")
    print()

    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_FROM, TWILIO_PHONE_TO]):
        print("ERROR: Missing Twilio credentials. Please set environment variables.")
        return False

    try:
        print("Connecting to Twilio...")
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        print("Sending test SMS...")
        message = client.messages.create(
            body="🧪 Test message from Mountain Warehouse Monitor - If you receive this, SMS is working correctly!",
            from_=TWILIO_PHONE_FROM,
            to=TWILIO_PHONE_TO
        )

        print(f"\n✓ SUCCESS!")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        print(f"From: {message.from_}")
        print(f"To: {message.to}")
        print(f"\nCheck your phone for the test message!")

        return True

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        print("\nCommon issues:")
        print("1. Wrong Account SID or Auth Token")
        print("2. Phone numbers not in E.164 format (should be: +1234567890)")
        print("3. For trial accounts: 'To' number must be verified in Twilio console")
        print("4. 'From' number must be a valid Twilio number you own")
        return False

if __name__ == "__main__":
    test_sms()
