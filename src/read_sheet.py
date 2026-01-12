import os
import csv
import requests
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

load_dotenv()  # ✅ load .env as soon as module is imported

def parse_day(s: str) -> date:
    s = (s or "").strip()
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Unrecognized day format: '{s}'")

from datetime import datetime

def normalize_time(s: str) -> str:
    """
    Normalize times to zero-padded UI format.

    Examples:
      '2:00 PM'       -> '02:00 PM'
      '02:00 PM'      -> '02:00 PM'
      '02:00:00 PM'   -> '02:00 PM'
    """
    if not s:
        return s

    s = s.strip()

    for fmt in ("%I:%M:%S %p", "%I:%M %p"):
        try:
            dt = datetime.strptime(s, fmt)
            # %I keeps leading zero
            return dt.strftime("%I:%M %p")
        except ValueError:
            continue

    return s


def get_request_for_days_away(days_away: int = 3):
    sheet_url = os.getenv("GOOGLE_SHEET_CSV_URL")
    if not sheet_url:
        raise RuntimeError("GOOGLE_SHEET_CSV_URL not set (check .env)")

    target = date.today() + timedelta(days=days_away)

    r = requests.get(sheet_url, timeout=20)
    r.raise_for_status()

    rows = list(csv.DictReader(r.text.splitlines()))
    matches = []

    for row in rows:
        day_cell = row.get("Day")
        if not day_cell:
            continue

        try:
            d = parse_day(day_cell)
        except ValueError:
            continue

        if d == target:
            matches.append(row)

    if not matches:
        return None

    top = matches[0]  # earliest submission wins

    kerb = (top.get("kerb") or "").strip()
    return {
        "date": target.isoformat(),
        "start_time": normalize_time(top.get("Start time")),
        "end_time": normalize_time(top.get("End Time")),
        "kerb": kerb,
        "email": f"{kerb}@mit.edu" if kerb else None,
    }
