import os
from datetime import date, timedelta
import calendar
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from src.config import get_config
from src.browser import launch_browser, new_context, save_state

URL = "https://mit.clubautomation.com/event/reserve-court-new"
STORAGE_STATE_PATH = "storage_state.json"

def is_logged_in(page) -> bool:
    body = page.locator("body").inner_text(timeout=5000)
    return not (("Log In" in body) or ("Login" in body) or ("Sign In" in body))

def login_if_needed(page, cfg):
    if is_logged_in(page):
        return

    try:
        page.get_by_test_id("loginAccountPassword").wait_for(timeout=4000)
    except PlaywrightTimeoutError:
        return

    for possible_user_id in ["loginAccountUsername", "loginAccountEmail", "loginAccountLogin"]:
        try:
            page.get_by_test_id(possible_user_id).fill(cfg.username, timeout=800)
            break
        except Exception:
            pass

    page.get_by_test_id("loginAccountPassword").fill(cfg.password)
    page.get_by_test_id("loginAccountPassword").press("Enter")
    page.get_by_test_id("loginFormSubmitButton").click()
    page.wait_for_load_state("networkidle")

def goto_reservations(page):
    page.get_by_role("link", name="Reservations").click()
    page.wait_for_load_state("networkidle")

def select_tennis(page):
    page.locator("a").filter(has_text="Swimming").click()
    page.locator("#component_chosen").get_by_text("Tennis", exact=True).click()

def open_reserve_court(page):
    page.get_by_role("cell", name="Your Reservations Host").get_by_role("link").nth(2).click()
    page.wait_for_load_state("networkidle")

def month_year_label(d: date) -> str:
    return f"{calendar.month_name[d.month]}, {d.year}"

def reopen_reserve_panel(page):
    page.get_by_role("cell", name="Your Reservations Host").get_by_role("link").click()
    page.wait_for_timeout(300)  # tiny delay so calendar DOM is interactive

def set_date_and_times(page, days_from_today: int, time_from: str, time_to: str):
    today = date.today()
    target = today + timedelta(days=days_from_today)
    
    # Format date as MM/DD/YYYY (e.g., "01/02/2026")
    date_str = target.strftime("%m/%d/%Y")

    # 1) Double-click the date field to select all
    page.locator("#date").dblclick()
    
    # 2) Press ArrowRight 11 times to position cursor (as per working example)
    for _ in range(11):
        page.locator("#date").press("ArrowRight")
    
    # 3) Fill with the target date in MM/DD/YYYY format
    page.locator("#date").fill(date_str)
    page.wait_for_timeout(200)  # Small delay after filling date

    # 5) Times (Chosen)
    page.locator("#timeFrom_chosen a").click()
    page.locator("#timeFrom_chosen .chosen-results").get_by_text(time_from, exact=True).click()

    page.locator("#timeTo_chosen a").click()
    page.locator("#timeTo_chosen .chosen-results").get_by_text(time_to, exact=True).click()



def run_booking(days_from_today: int, time_from: str, time_to: str, headless: bool = True):
    """
    Returns: (success: bool, screenshot_path: str, details: str)
    NOTE: Right now this runs through Search and screenshots results.
    If you already have the final 'click slot -> confirm booking' steps,
    insert them where indicated below.
    """
    cfg = get_config()

    p, browser = launch_browser(headless=headless)
    context = new_context(browser)
    page = context.new_page()

    success_shot = "booking_success.png"
    fail_shot = "booking_failed.png"

    try:
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(800)

        login_if_needed(page, cfg)

        if not os.path.exists(STORAGE_STATE_PATH) and is_logged_in(page):
            save_state(context)

        goto_reservations(page)
        select_tennis(page)
        # Skip open_reserve_court() - the working sequence goes directly to clicking #date

        set_date_and_times(page, days_from_today=days_from_today, time_from=time_from, time_to=time_to)

        page.get_by_role("button", name="Search").click()
        page.wait_for_load_state("networkidle")

        try:
            page.get_by_role("link", name=":00pm").click(timeout=3000)
        except Exception:
            page.screenshot(path=fail_shot, full_page=True)
            return False, fail_shot, "Failed to book: no ':00pm' slot link found/clickable."

        # 2) Confirm
        try:
            page.get_by_role("button", name="Confirm").click(timeout=5000)
            # 3) Ok
            page.get_by_role("button", name="Ok").click(timeout=5000)
        except Exception as e:
            page.screenshot(path=fail_shot, full_page=True)
            return False, fail_shot, f"Failed during Confirm/Ok: {e}"

        # 4) Wait 3 seconds for UI to settle
        page.wait_for_timeout(3000)

        # 5) Screenshot after success flow
        page.screenshot(path=success_shot, full_page=True)
        return True, success_shot, "Booked successfully (slot click → Confirm → Ok)."

    except Exception as e:
        try:
            page.screenshot(path=fail_shot, full_page=True)
        except Exception:
            pass
        return False, fail_shot, f"Exception: {e}"

    finally:
        context.close()
        browser.close()
        p.stop()
