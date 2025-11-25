# Mountain Warehouse PLP Monitor

Automated monitoring system that checks Mountain Warehouse PLP (Product Listing Page) pages every 10 minutes to ensure a minimum number of sub-categories are present.

## Features

- ✅ Monitors 9 PLP pages automatically every 10 minutes
- ✅ Sends SMS alerts via Twilio when sub-categories drop below threshold (minimum 6)
- ✅ Alert-once mechanism (only alerts once per issue, not repeatedly)
- ✅ Tracks alert state across runs
- ✅ Runs on GitHub Actions (works when your machine is off)
- ✅ Logs recovery when pages return to normal

## Monitored Pages

1. https://www.mountainwarehouse.com/eu/mens/
2. https://www.mountainwarehouse.com/eu/womens/
3. https://www.mountainwarehouse.com/eu/kids/
4. https://www.mountainwarehouse.com/eu/footwear/
5. https://www.mountainwarehouse.com/eu/equipment/
6. https://www.mountainwarehouse.com/eu/by-activity/
7. https://www.mountainwarehouse.com/eu/camping/
8. https://www.mountainwarehouse.com/eu/ski/
9. https://www.mountainwarehouse.com/eu/clearance/

## Setup Instructions

### 1. Get Twilio Credentials

If you don't have a Twilio account yet:
1. Sign up at https://www.twilio.com/try-twilio
2. Get a free trial phone number
3. Find your credentials at https://console.twilio.com/

You'll need:
- **Account SID** (starts with `AC...`)
- **Auth Token**
- **Twilio Phone Number** (your Twilio number, format: +1234567890)
- **Your Phone Number** (where to receive alerts, format: +1234567890)

### 2. Configure GitHub Secrets

Add your Twilio credentials as GitHub repository secrets:

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add each of these:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID | `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token | `your_auth_token_here` |
| `TWILIO_PHONE_FROM` | Your Twilio phone number | `+15551234567` |
| `TWILIO_PHONE_TO` | Your phone number (to receive alerts) | `+15559876543` |

### 3. Enable GitHub Actions

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. If prompted, enable GitHub Actions for this repository
4. The workflow will now run automatically every 10 minutes

### 4. Test the Setup

You can manually trigger a test run:

1. Go to **Actions** tab in your GitHub repository
2. Click on **Mountain Warehouse PLP Monitor** workflow
3. Click **Run workflow** → **Run workflow**
4. Wait for the job to complete and check the logs

## How It Works

### Monitoring Process

1. **Every 10 minutes**, GitHub Actions runs the monitoring script
2. The script fetches all 9 PLP pages
3. It counts sub-categories using CSS selector: `a[class*="CategoryTile_categoryTile"]`
4. If any page has **less than 6 sub-categories**:
   - An SMS alert is sent via Twilio (first time only)
   - Alert state is saved to prevent repeat alerts
5. When the page recovers (6+ sub-categories), the alert state is reset
   - The system will log the recovery but won't send an SMS
   - It can now alert again if the issue reoccurs

### Alert State Tracking

The `alert_state.json` file tracks which URLs have been alerted:

```json
{
  "https://www.mountainwarehouse.com/eu/mens/": {
    "alerted": true,
    "timestamp": "2025-11-25T10:30:00",
    "count": 4
  }
}
```

This file is automatically committed back to the repository after each run.

## Files

- **`monitor.py`** - Main monitoring script
- **`requirements.txt`** - Python dependencies
- **`.github/workflows/monitor.yml`** - GitHub Actions workflow configuration
- **`alert_state.json`** - Tracks alert state (auto-generated)
- **`README.md`** - This file

## Monitoring Logs

To view monitoring logs:

1. Go to **Actions** tab in GitHub
2. Click on any workflow run
3. Click on the **monitor** job
4. Expand **Run monitoring script** to see detailed logs

Example log output:
```
============================================================
Mountain Warehouse PLP Monitor
Run time: 2025-11-25 10:30:00 UTC
============================================================

Checking: mens (https://www.mountainwarehouse.com/eu/mens/)
  Found 8 subcategories
  ✓ OK

Checking: womens (https://www.mountainwarehouse.com/eu/womens/)
  Found 4 subcategories
  ⚠ WARNING: Below minimum (6)

...
```

## Troubleshooting

### No SMS received

1. Check GitHub Actions logs for errors
2. Verify Twilio credentials are correct in GitHub Secrets
3. Check phone numbers are in correct format: `+1234567890`
4. For Twilio trial accounts, verify your phone number is verified
5. Check Twilio console for SMS logs: https://console.twilio.com/

### Workflow not running

1. Ensure GitHub Actions is enabled for the repository
2. Check the **Actions** tab for any errors
3. Verify the workflow file is in `.github/workflows/monitor.yml`
4. GitHub Actions has usage limits on free accounts (check your quota)

### Script errors

- Check the workflow logs in GitHub Actions
- Test locally: `python monitor.py` (requires credentials in environment)
- Review error messages in the GitHub Actions output

## Local Testing

To test the script locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TWILIO_ACCOUNT_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_PHONE_FROM="+1234567890"
export TWILIO_PHONE_TO="+1234567890"

# Run the script
python monitor.py
```

## Customization

### Change monitoring interval

Edit `.github/workflows/monitor.yml`:

```yaml
schedule:
  - cron: '*/10 * * * *'  # Every 10 minutes
  # - cron: '*/5 * * * *'   # Every 5 minutes
  # - cron: '0 * * * *'     # Every hour
```

### Change minimum sub-category threshold

Edit `monitor.py`:

```python
MIN_SUBCATEGORIES = 6  # Change this value
```

### Add/remove URLs

Edit the `URLS_TO_MONITOR` list in `monitor.py`:

```python
URLS_TO_MONITOR = [
    "https://www.mountainwarehouse.com/eu/mens/",
    # Add more URLs here
]
```

## Cost

- **GitHub Actions**: Free for public repositories (2,000 minutes/month for private repos)
- **Twilio**: Trial account provides free credits; pay-as-you-go after ($0.0075 per SMS)

## Support

For issues or questions:
1. Check the workflow logs in GitHub Actions
2. Review this README
3. Test locally to isolate the problem

## License

This monitoring system is provided as-is for internal use.
