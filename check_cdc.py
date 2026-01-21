import requests
import json
import os
from pathlib import Path

API_URL = "https://enrol.cdc.com.sg/wscdctestdate/api/testsate/"
STATE_FILE = "last_date.json"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    })

# Load last notified date
last_date = None
if Path(STATE_FILE).exists():
    with open(STATE_FILE) as f:
        last_date = json.load(f).get("date")

# Fetch CDC API
resp = requests.get(API_URL, timeout=10)
data = resp.json()

# Find THEORY TEST DATE block
theory = next(
    item for item in data
    if item.get("name") == "THEORY TEST DATE"
)

# Find Class 2B Riding Theory Test
course = next(
    c for c in theory["courses"]
    if c["description"] == "Class 2B Riding Theory Test"
)

date = course["date"]
day = course["day"]

# Ignore placeholder
if date == "Please check the next working day.":
    print("No slot yet.")
    exit(0)

# Prevent duplicate alerts
if date == last_date:
    print("No change.")
    exit(0)

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
