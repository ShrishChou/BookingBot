import sys, os
sys.path.append(os.path.dirname(__file__))

from email_notify import send_email

send_email(
    to_email="shrishc@mit.edu",
    subject="BookingBot test email",
    body="If you got this, SMTP works 🎉",
)
