from playwright.sync_api import sync_playwright
print("A browser will open. Sign in to LinkedIn, then close the browser window.")
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(".jobnova_browser_profile", headless=False, args=["--start-maximized"], viewport=None)
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://www.linkedin.com/login")
    try:
        page.wait_for_event("close", timeout=0)
    except Exception:
        pass
