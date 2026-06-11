from playwright.sync_api import sync_playwright

def test_clicks():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:5000/")
        
        # Click theme toggle
        print("Clicking theme toggle...")
        page.click("#theme-toggle")
        
        # Wait a bit for transitions
        page.waitForTimeout(500)
        
        # Try to click chatbot toggle
        print("Clicking chatbot toggle...")
        try:
            page.click("#chatbot-toggle", timeout=2000)
            print("Successfully clicked chatbot toggle!")
        except Exception as e:
            print(f"Failed to click: {e}")
            
        browser.close()

if __name__ == "__main__":
    test_clicks()
