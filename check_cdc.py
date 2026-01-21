import requests
import os
from datetime import datetime

API_URL = "https://enrol.cdc.com.sg/wscdctestdate/api/testdate/"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError("BOT_TOKEN or CHAT_ID not set")

resp = requests.get(API_URL, timeout=10)

try:
    data = resp.json()
except Exception:
    print("Non-JSON response from API")
    print(resp.text[:300])
    exit(0)

for course in data.get("courses", []):
    if course.get("description") == "Class 2B Riding Theory Test":
        date = course.get("date", "").strip()

        if date == "Please check the next working day.":
            message = "No slot yet."
        else:
            try:
                day = datetime.strptime(date, "%d/%m/%Y").strftime("%A")
            except Exception:
                day = "Unknown"

            message = (
                "🚨 *Class 2B Riding Theory Test Slot Available!*\n\n"
                f"📅 *Date:* {date}\n"
                f"📆 *Day:* {day}"
            )

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            },
            timeout=10
        )

        break
