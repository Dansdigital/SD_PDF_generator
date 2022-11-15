import time
from playwright.sync_api import Playwright, sync_playwright, expect

def login(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width":800,"height":600})
    # Open new page
    page = context.new_page()
    page.goto("https://straydogstrength.com/login-and-register/")

    # Click input[name="log"]
    page.locator("input[name=\"log\"]").click()
    # Fill input[name="log"]
    page.locator("input[name=\"log\"]").fill("#####")
    # Click input[name="pwd"]
    page.locator("input[name=\"pwd\"]").click()
    # Fill input[name="pwd"]
    page.locator("input[name=\"pwd\"]").fill("######")
    page.locator("#wp-submit").click()
    # Save storage state into the file.
    storage = context.storage_state(path="state.json")
    print(storage)
    # Create a new context with the saved storage state.
    context = browser.new_context(storage_state="state.json")

with sync_playwright() as playwright:
    login(playwright)
    time.sleep(5)


