import requests
import json
import os
from pathlib import Path
import sys

API_URL = "https://enrol.cdc.com.sg/wscdctestdate/api/testdate/"
STATE_FILE = "last_date.json"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    })
    r.raise_for_status()

# Load last notified date
last_date = None
if Path(STATE_FILE).exists():
    with open(STATE_FILE) as f:
        last_date = json.load(f).get("date")

# Fetch CDC API
resp = requests.get(API_URL, headers=HEADERS, timeout=15)

if resp.status_code != 200 or not resp.text.strip():
    print(f"CDC API error: status={resp.status_code}")
    sys.exit(0)  # don't fail the workflow

try:
    data = resp.json()
except Exception as e:
    print("Failed to parse JSON:")
    print(resp.text[:500])
    sys.exit(0)

# Find THEORY TEST DATE block
theory = next(
    (item for item in data if item.get("name") == "THEORY TEST DATE"),
    None
)

if not theory:
    print("THEORY TEST DATE not found.")
    sys.exit(0)

# Find Class 2B Riding Theory Test
course = next(
    (c for c in theory.get("courses", [])
     if c.get("description") == "Class 2B Riding Theory Test"),
    None
)

if not course:
    print("Class 2B Riding Theory Test not found.")
    sys.exit(0)

date = course.get("date", "")
day = course.get("day", "")

# Ignore placeholder
if date == "Please check the next working day.":
    print("No slot yet.")
    sys.exit(0)

# Prevent duplicate alerts
if date == last_date:
    print("No change.")
    sys.exit(0)

# Alert!
message = (
    "🚨 *Class 2B Riding Theory Test Slot Available!*\n\n"
    f"📅 *Date:* {date}\n"
    f"📆 *Day:* {day}"
)
send_telegram(message)

# Save state
with open(STATE_FILE, "w") as f:
    json.dump({"date": date}, f)

print("Alert sent.")
