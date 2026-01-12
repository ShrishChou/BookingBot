import os
from playwright.sync_api import sync_playwright, Browser, BrowserContext

STORAGE_STATE_PATH = "storage_state.json"

def launch_browser(headless: bool):
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=headless)
    return p, browser

def new_context(browser: Browser) -> BrowserContext:
    """
    If storage_state.json exists, reuse it (logged-in session).
    Otherwise create a fresh context.
    """
    if os.path.exists(STORAGE_STATE_PATH):
        return browser.new_context(storage_state=STORAGE_STATE_PATH)
    return browser.new_context()

def save_state(context: BrowserContext):
    context.storage_state(path=STORAGE_STATE_PATH)
