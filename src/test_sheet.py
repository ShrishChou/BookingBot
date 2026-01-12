import os
import csv
import requests
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def parse_day(s: str) -> date:
    s = (s or "").strip()
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Unrecognized day format: '{s}'")

def normalize_time(s: str) -> str:
    """
    Convert '5:00:00 PM' -> '5:00 PM' and keep AM/PM.
    """
    s = (s or "").strip()
    for fmt in ("%I:%M:%S %p", "%I:%M %p"):
        try:
            t = datetime.strptime(s, fmt).strftime("%-I:%M %p")
            return t
        except ValueError:
            pass
    return s  # fallback

def main():
    url = os.getenv("GOOGLE_SHEET_CSV_URL")
    if not url:
        raise RuntimeError("Missing GOOGLE_SHEET_CSV_URL in .env")

    print("Fetching CSV from:", url)
    r = requests.get(url, timeout=20)
    print("HTTP status:", r.status_code)
    r.raise_for_status()

    lines = r.text.splitlines()
    print("CSV lines:", len(lines))
    if len(lines) < 2:
        print("CSV returned header only (no rows).")
        return

    reader = csv.DictReader(lines)
    rows = list(reader)

    print("\nDetected columns:", reader.fieldnames)
    print("Total rows:", len(rows))

    print("\nLast 3 rows (sanity check):")
    for row in rows[-3:]:
        print({
            "Timestamp": row.get("Timestamp"),
            "Day": row.get("Day"),
            "Start time": row.get("Start time"),
            "End Time": row.get("End Time"),
            "kerb": row.get("kerb"),
        })

    target = date.today() + timedelta(days=3)
    print("\nTarget date (today + 3):", target.isoformat())

    matches = []
    for row in rows:
        day_cell = row.get("Day")
        if not day_cell:
            continue
        d = parse_day(day_cell)
        if d == target:
            matches.append(row)

    if not matches:
        print("❌ No matching bookings found for target date.")
        return

    top = matches[0]
    kerb = (top.get("kerb") or "").strip()
    start_time = normalize_time(top.get("Start time"))
    end_time = normalize_time(top.get("End Time"))

    print("\n✅ Selected TOP booking:")
    print({
        "kerb": kerb,
        "email_inferred": f"{kerb}@mit.edu" if kerb else None,
        "day": target.isoformat(),
        "start_time": start_time,
        "end_time": end_time,
    })

if __name__ == "__main__":
    main()
