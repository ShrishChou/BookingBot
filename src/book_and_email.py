import json
from pathlib import Path
from datetime import datetime, date

from src.bookingbot import run_booking
from src.email_notify import send_email

PENDING = Path("pending_request.json")

def main():
    if not PENDING.exists():
        print("pending_request.json not found (run prefetch first).")
        return

    payload = json.loads(PENDING.read_text())
    if not payload.get("found"):
        print("No pending request to book.")
        return

    req = payload["request"]
    email = req["email"]
    start_time = req["start_time"]
    end_time = req["end_time"]
    day_iso = req["date"]

    # Calculate days_from_today from the actual date in the JSON
    target_date = date.fromisoformat(day_iso)
    today = date.today()
    days_from_today = (target_date - today).days

    print(f"Booking for date: {day_iso} ({days_from_today} days from today)")

    success, screenshot, details = run_booking(
        days_from_today=days_from_today,
        time_from=start_time,
        time_to=end_time,
        headless=False,
    )

    subject = "Court booked successfully" if success else "Court booking failed"
    body = (
        f"Booking request\n"
        f"Date: {day_iso}\n"
        f"Time window: {start_time} – {end_time}\n"
        f"Kerb: {req['kerb']}\n\n"
        f"Result: {'SUCCESS' if success else 'FAILED'}\n"
        f"Details: {details}\n"
        f"Timestamp: {datetime.now().isoformat(timespec='seconds')}\n"
    )

    send_email(
        to_email=email,
        subject=subject,
        body=body,
        attachment_path=screenshot,
    )
    print("Emailed:", email, "| success:", success, "| screenshot:", screenshot)

if __name__ == "__main__":
    main()
