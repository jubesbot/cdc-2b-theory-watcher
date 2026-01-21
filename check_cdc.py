import requests
import os
from datetime import datetime

API_URL = "https://enrol.cdc.com.sg/wscdctestdate/api/testdate/"
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

resp = requests.get(API_URL, timeout=10)
data = resp.json()

for course in data.get("courses", []):
    if course.get("description") == "Class 2B Riding Theory Test":
        date = course.get("date", "").strip()

        if date == "Please check the next working day.":
            message = "No slot yet."
        else:
            try:
                dt = datetime.strptime(date, "%d/%m/%Y")
                day = dt.strftime("%A")
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
            }
        )

        break
