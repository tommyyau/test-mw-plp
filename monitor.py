#!/usr/bin/env python3
"""
Mountain Warehouse PLP Monitoring Script
Monitors PLP pages for sub-category count and sends alerts via Twilio
"""

import os
import json
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from twilio.rest import Client

# Configuration
URLS_TO_MONITOR = [
    "https://www.mountainwarehouse.com/eu/mens/",
    "https://www.mountainwarehouse.com/eu/womens/",
    "https://www.mountainwarehouse.com/eu/kids/",
    "https://www.mountainwarehouse.com/eu/footwear/",
    "https://www.mountainwarehouse.com/eu/equipment/",
    "https://www.mountainwarehouse.com/eu/by-activity/",
    "https://www.mountainwarehouse.com/eu/camping/",
    "https://www.mountainwarehouse.com/eu/ski/",
    "https://www.mountainwarehouse.com/eu/clearance/",
]

SUBCATEGORY_SELECTOR = 'a[class*="CategoryTile_categoryTile"]'
MIN_SUBCATEGORIES = 8
ALERT_STATE_FILE = "alert_state.json"

# Twilio configuration from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_FROM = os.getenv("TWILIO_PHONE_FROM")
TWILIO_PHONE_TO = os.getenv("TWILIO_PHONE_TO")


def load_alert_state():
    """Load the alert state from file"""
    if os.path.exists(ALERT_STATE_FILE):
        with open(ALERT_STATE_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_alert_state(state):
    """Save the alert state to file"""
    with open(ALERT_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def count_subcategories(page, url):
    """
    Fetch a URL and count subcategories using the CSS selector
    Returns (count, error_message) tuple
    """
    try:
        # Navigate to the page
        page.goto(url, wait_until="networkidle", timeout=60000)

        # Wait for category tiles to load
        page.wait_for_selector(SUBCATEGORY_SELECTOR, timeout=30000)

        # Get page content
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        subcategories = soup.select(SUBCATEGORY_SELECTOR)

        return len(subcategories), None

    except PlaywrightTimeout as e:
        return 0, f"Timeout loading page: {str(e)}"
    except Exception as e:
        return 0, f"Error: {str(e)}"


def send_twilio_alert(message):
    """Send SMS alert via Twilio"""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_FROM, TWILIO_PHONE_TO]):
        print("ERROR: Twilio credentials not configured")
        return False

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        sms = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_FROM,
            to=TWILIO_PHONE_TO
        )

        print(f"✓ SMS sent successfully (SID: {sms.sid})")
        return True

    except Exception as e:
        print(f"ERROR sending SMS: {str(e)}")
        return False


def main():
    """Main monitoring function"""
    print(f"\n{'='*60}")
    print(f"Mountain Warehouse PLP Monitor")
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*60}\n")

    alert_state = load_alert_state()
    issues_found = []
    recoveries = []

    # Launch browser with Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        for url in URLS_TO_MONITOR:
            page_name = url.split('/')[-2]
            print(f"Checking: {page_name} ({url})")

            count, error = count_subcategories(page, url)

            if error:
                print(f"  ✗ ERROR: {error}")
                issues_found.append(f"{page_name}: {error}")
                continue

            print(f"  Found {count} subcategories")

            # Check if subcategories dropped below threshold
            if count < MIN_SUBCATEGORIES:
                print(f"  ⚠ WARNING: Below minimum ({MIN_SUBCATEGORIES})")

                # Only alert if we haven't alerted for this URL yet
                if not alert_state.get(url, {}).get('alerted', False):
                    issues_found.append(f"{page_name}: {count} subcategories (minimum: {MIN_SUBCATEGORIES})")
                    alert_state[url] = {
                        'alerted': True,
                        'timestamp': datetime.now().isoformat(),
                        'count': count
                    }
                else:
                    print(f"  (Already alerted previously)")
            else:
                print(f"  ✓ OK")

                # Check if this URL has recovered
                if alert_state.get(url, {}).get('alerted', False):
                    recoveries.append(f"{page_name}: Recovered to {count} subcategories")
                    alert_state[url] = {
                        'alerted': False,
                        'timestamp': datetime.now().isoformat(),
                        'count': count
                    }

        browser.close()

    # Send alerts if there are new issues
    if issues_found:
        # Keep message short for SMS limits (70 chars with emoji/unicode)
        message = f"MW Alert: {len(issues_found)} page(s) <{MIN_SUBCATEGORIES} cats\n"
        message += "\n".join(f"{issue.split(':')[0]}: {issue.split(':')[1].split()[0]}" for issue in issues_found)

        print(f"\n{'='*60}")
        print("SENDING ALERT:")
        print(message)
        print(f"{'='*60}\n")

        send_twilio_alert(message)

    # Log recoveries (but don't send SMS for recoveries)
    if recoveries:
        print(f"\n{'='*60}")
        print("RECOVERIES DETECTED:")
        for recovery in recoveries:
            print(f"  ✓ {recovery}")
        print(f"{'='*60}\n")

    # Save updated alert state
    save_alert_state(alert_state)

    print(f"\nMonitoring complete. Next check in 20 minutes.\n")

    # Exit with error code if there are issues (for GitHub Actions visibility)
    if issues_found:
        sys.exit(1)


if __name__ == "__main__":
    main()
