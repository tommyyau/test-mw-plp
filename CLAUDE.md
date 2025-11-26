# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an automated monitoring system that checks Mountain Warehouse Product Listing Pages (PLPs) every 20 minutes to ensure a minimum number of sub-categories are present. It runs on GitHub Actions and sends SMS alerts via Twilio when thresholds are breached.

## Key Commands

### Local Development and Testing

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers (required for web scraping)
playwright install chromium
playwright install-deps chromium

# Run the monitoring script locally (requires Twilio env vars)
python monitor.py
```

### Environment Variables (Required for Local Testing)

```bash
export TWILIO_ACCOUNT_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_PHONE_FROM="+1234567890"
export TWILIO_PHONE_TO="+1234567890"
```

## Architecture

### Core Components

**monitor.py** - Main monitoring script with three key responsibilities:
1. **Web Scraping**: Uses Playwright (headless Chromium) to fetch PLP pages and parse HTML with BeautifulSoup
2. **Alert State Management**: Tracks which URLs have been alerted in `alert_state.json` to prevent duplicate alerts
3. **SMS Notifications**: Sends alerts via Twilio REST API when subcategory count drops below threshold

**Alert State Mechanism**:
- Alerts are sent only ONCE when a page first drops below threshold (monitor.py:139-145)
- State is persisted in `alert_state.json` and committed back to repo after each run
- When a page recovers (meets threshold again), the alert state is reset, enabling future alerts (monitor.py:152-158)
- Recoveries are logged but do NOT trigger SMS notifications

### Monitoring Flow

1. Script runs every 20 minutes via GitHub Actions cron schedule
2. For each URL in `URLS_TO_MONITOR`:
   - Playwright loads the page with custom user agent to avoid bot detection
   - Waits for category tiles to load (selector: `a[class*="CategoryTile_categoryTile"]`)
   - BeautifulSoup counts matching elements
3. If count < `MIN_SUBCATEGORIES` (currently 8):
   - Check `alert_state.json` to see if already alerted
   - If new issue: send SMS via Twilio and mark as alerted
   - If already alerted: skip SMS, just log
4. If count >= `MIN_SUBCATEGORIES` and previously alerted:
   - Log recovery and reset alert state (no SMS)
5. GitHub Actions commits updated `alert_state.json` back to repo

### GitHub Actions Integration

**Workflow file**: `.github/workflows/monitor.yml`

Key workflow features:
- Runs on schedule (every 20 minutes), manual trigger, and push to main/claude/** branches
- Uses `continue-on-error: true` on monitoring step so failures don't prevent state commits
- Commits are tagged with `[skip ci]` to prevent infinite workflow loops
- Twilio credentials loaded from GitHub Secrets

## Configuration

### Key Constants in monitor.py

- `URLS_TO_MONITOR` (line 16): List of 9 PLP URLs to check
- `SUBCATEGORY_SELECTOR` (line 28): CSS selector for category tiles
- `MIN_SUBCATEGORIES` (line 29): Alert threshold (currently 8)
- `ALERT_STATE_FILE` (line 30): JSON file tracking alert state

### Modifying Monitoring Behavior

**Change check frequency**: Edit cron schedule in `.github/workflows/monitor.yml:6`

**Change alert threshold**: Modify `MIN_SUBCATEGORIES` in `monitor.py:29`

**Add/remove URLs**: Update `URLS_TO_MONITOR` list in `monitor.py:16-26`

**Change CSS selector**: Update `SUBCATEGORY_SELECTOR` in `monitor.py:28` if site structure changes

## Important Implementation Notes

- Playwright is used instead of simple HTTP requests because the site likely has bot protection
- Custom user agent (monitor.py:117) mimics a real Chrome browser
- `wait_until="networkidle"` ensures page is fully loaded before parsing
- Script exits with code 1 if issues found (monitor.py:190) for GitHub Actions visibility
- Alert state persistence is critical - it prevents SMS spam and maintains state across workflow runs
