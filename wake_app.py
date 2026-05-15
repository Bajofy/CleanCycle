import os
import time
from playwright.sync_api import sync_playwright

# Fallback to standard Streamlit URL scheme if env variable is not set
URL = os.environ.get("STREAMLIT_APP_URL", "https://cleancycle.streamlit.app/")

def main():
    print(f"Navigating to {URL}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate and wait for content to stabilize
        page.goto(URL, wait_until="networkidle")
        time.sleep(5)
        
        # Look for the 'Yes, get this app back up!' button text
        wake_button = page.locator("button:has-text('app back up')").first
        
        if wake_button.is_visible():
            print("App is asleep! Clicking the wake-up button...")
            wake_button.click()
            print("Button clicked. Waiting 15 seconds for boot sequence...")
            time.sleep(15)
        else:
            print("App appears to be awake or loading normally.")
            
        browser.close()

if __name__ == "__main__":
    main()
