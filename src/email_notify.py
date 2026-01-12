import os
import smtplib
import mimetypes
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv

# Load .env automatically
load_dotenv()

def send_email(to_email, subject, body, attachment_path=None):
    msg = EmailMessage()
    msg["From"] = os.environ["EMAIL_FROM"]
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    if attachment_path:
        p = Path(attachment_path)
        if p.exists():
            mime, _ = mimetypes.guess_type(p)
            maintype, subtype = (mime or "application/octet-stream").split("/", 1)
            msg.add_attachment(
                p.read_bytes(),
                maintype=maintype,
                subtype=subtype,
                filename=p.name,
            )

    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"])) as s:
        s.starttls()
        s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        s.send_message(msg)
