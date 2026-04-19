from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://facebook.com")
    print("Log in manually, then wait 30 seconds...")
    page.wait_for_timeout(120000)

    context.storage_state(path="state.json")
    browser.close()