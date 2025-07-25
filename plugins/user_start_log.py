import json
import os
from datetime import datetime, timedelta
from pytz import timezone
from config import *
from pyrogram import Client, filters

# India timezone (UTC+5:30)
IST = timezone("Asia/Kolkata")

def log_start_usage(user_id):
    now_ist = datetime.now(IST)
    date_str = now_ist.strftime("%Y-%m-%d")
    time_str = now_ist.strftime("%H:%M:%S")

    entry = {
        "user_id": user_id,
        "date": date_str,
        "time": time_str
    }

    if not os.path.exists(USER_LOG_FILE):
        with open(USER_LOG_FILE, "w") as f:
            json.dump([], f)

    with open(USER_LOG_FILE, "r") as f:
        data = json.load(f)

    data.append(entry)

    with open(USER_LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_start_stats():
    now_ist = datetime.now(IST).date()
    days = {
        "Today": now_ist,
        "Yesterday": now_ist - timedelta(days=1),
        "Day Before": now_ist - timedelta(days=2)
    }

    counts = {label: 0 for label in days}

    if not os.path.exists(USER_LOG_FILE):
        return counts

    with open(USER_LOG_FILE, "r") as f:
        data = json.load(f)

    for entry in data:
        try:
            entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()
            for label, day in days.items():
                if entry_date == day:
                    counts[label] += 1
        except:
            continue

    return counts

