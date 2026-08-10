# BookingBot

**A scheduled booking agent: read requests from a Google Sheet, drive the booking site in a real browser, confirm by email.**

Some reservations open on a fixed schedule and are gone within seconds. That is not a problem you solve by being attentive; it is one you solve by not being human at the moment it matters. BookingBot watches a Google Sheet for requests, prefetches everything it can in advance, executes the booking through browser automation the instant the window opens, and emails the outcome.

Requests are submitted through a [Google Form](https://docs.google.com/forms/d/e/1FAIpQLSc5slAqWQ7H6XGYbm3D0dXjaM3LHf1ec_tl-4BL9MU4OmnExg/viewform).

---

## Design

```
Google Form  →  Google Sheet  →  prefetch  →  book  →  email confirmation
```

The **prefetch/book split** is the point. Session setup, authentication and page loads are slow and can all be done *before* the booking window opens; only the final commit is time-critical. Separating them means the latency that counts is a single click, not a cold start.

| file | role |
|---|---|
| `src/bookingbot.py` | booking logic |
| `src/prefetch.py` | warm sessions and pages ahead of the window |
| `src/book_and_email.py` | end-to-end: book, then notify |
| `src/browser.py` | browser automation driver |
| `src/read_sheet.py` | pull pending requests from the Google Sheet |
| `src/email_notify.py` | confirmation email |
| `src/config.py` | credentials and settings |
| `src/testbook.py`, `src/test_sheet.py` | integration checks against the live services |
| `scripts/run_prefetch.sh`, `scripts/run_book_and_email.sh` | cron entry points |

## Running

```bash
pip install -r requirements.txt
# configure Google Sheets API credentials and email settings in src/config.py
./scripts/run_prefetch.sh          # warm the session ahead of the window
./scripts/run_book_and_email.sh    # book and notify
```

Both scripts are written to be driven from cron.

## Note

Credentials are read from local config and are not committed. This automates a personal booking workflow on a site the operator already has an account with — it is not a scraper or a bypass of anything.
