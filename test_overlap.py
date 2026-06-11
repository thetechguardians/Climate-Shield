from playwright.sync_api import sync_playwright

def check_overlaps():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:5000/Analysis/analysis.html")
        
        # Click theme toggle to switch to light mode
        page.click("#theme-toggle")
        page.wait_for_timeout(1000)
        
        # Evaluate element at the center of the chatbot toggle button
        element_info = page.evaluate("""() => {
            const btn = document.querySelector('#chatbot-toggle');
            if (!btn) return "Button not found";
            const rect = btn.getBoundingClientRect();
            const x = rect.left + rect.width / 2;
            const y = rect.top + rect.height / 2;
            const el = document.elementFromPoint(x, y);
            return el ? el.tagName + ' ' + el.className + ' id:' + el.id : 'No element';
        }""")
        
        print("Element intercepting chatbot toggle:", element_info)
        
        # Also check #demo-btn if it exists
        demo_info = page.evaluate("""() => {
            const btn = document.querySelector('#demo-btn');
            if (!btn) return "Demo Button not found";
            const rect = btn.getBoundingClientRect();
            const x = rect.left + rect.width / 2;
            const y = rect.top + rect.height / 2;
            const el = document.elementFromPoint(x, y);
            return el ? el.tagName + ' ' + el.className + ' id:' + el.id : 'No element';
        }""")
        print("Element intercepting demo toggle:", demo_info)
        
        # Also check analyze button
        analyze_info = page.evaluate("""() => {
            const btn = document.querySelector('.analyze-btn');
            if (!btn) return "Analyze Button not found";
            const rect = btn.getBoundingClientRect();
            const x = rect.left + rect.width / 2;
            const y = rect.top + rect.height / 2;
            const el = document.elementFromPoint(x, y);
            return el ? el.tagName + ' ' + el.className + ' id:' + el.id : 'No element';
        }""")
        print("Element intercepting analyze button:", analyze_info)
        
        browser.close()

if __name__ == "__main__":
    check_overlaps()
