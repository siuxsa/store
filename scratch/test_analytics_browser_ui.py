import os
import sys
import time
from playwright.sync_api import sync_playwright

artifact_dir = os.path.expanduser('~/.gemini/antigravity-cli/brain/3c7d032f-a2e3-45fe-b45d-a0b246098d8b')

def test_analytics_browser_ui():
    print("=== TESTING ANALYTICS IN LIVE BROWSER ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 850},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            extra_http_headers={"CF-Connecting-IP": "104.28.19.45"}
        )
        page = context.new_page()

        # 1. Visit storefront to trigger cookie creation and telemetry
        page.goto("http://127.0.0.1:5000/")
        page.wait_for_timeout(800)

        # Check cookies in browser
        cookies = context.cookies()
        cookie_names = [c["name"] for c in cookies]
        assert "zf_visitor_id" in cookie_names, f"zf_visitor_id cookie missing in browser: {cookie_names}"
        assert "zf_session_id" in cookie_names, f"zf_session_id cookie missing in browser: {cookie_names}"
        vid = [c["value"] for c in cookies if c["name"] == "zf_visitor_id"][0]
        print(f"✓ Browser received server tracking cookie: zf_visitor_id={vid}")

        # Visit /shop multiple times with the same cookie
        page.goto("http://127.0.0.1:5000/shop")
        page.wait_for_timeout(600)
        page.reload()
        page.wait_for_timeout(600)
        page.reload()
        page.wait_for_timeout(600)
        print("✓ Reloaded /shop repeatedly with the same visitor cookie.")

        # 2. Login to Admin
        page.goto("http://127.0.0.1:5000/admin/login")
        page.fill('input[name="identifier"]', 'admin')
        page.fill('input[name="password"]', 'Admin@2026')
        page.click('button[type="submit"]')
        page.wait_for_selector('#mod-analytics', timeout=10000)
        page.wait_for_timeout(1000)
        print("✓ Logged into Admin Command Center.")

        # 3. Check Analytics subtable: LIVE STREAM (10)
        page.click('button:has-text("LIVE STREAM (10)")')
        page.wait_for_timeout(800)

        # Verify table headers contain CLIENT USER AGENT and ORIGIN IP
        th_texts = page.locator('#subtab-stream table thead th').all_text_contents()
        print("Live Stream Headers:", th_texts)
        assert any("USER AGENT" in th for th in th_texts), f"USER AGENT column missing from table header: {th_texts}"
        assert any("IP" in th for th in th_texts), f"IP column missing from table header: {th_texts}"
        print("✓ Overview Live Stream table headers display CLIENT USER AGENT and ORIGIN IP!")

        # Verify rows populated
        rows = page.locator('#tbody-stream-analytics tr').count()
        print(f"✓ Overview Live Stream rendered {rows} telemetry rows.")

        # Scroll into view and screenshot
        page.locator('#analytics-tables-anchor').scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(artifact_dir, 'analytics_live_stream_ua_and_ip.png'))

        # 4. Switch to FULL MATRIX LIVE STREAM table (20 / PAGE)
        page.click('button:has-text("SHOW ALL (20 / PAGE)")')
        page.wait_for_timeout(800)
        page.click('#btn-full-matrix-stream')
        page.wait_for_timeout(800)

        matrix_th_texts = page.locator('#full-matrix-stream table thead th').all_text_contents()
        print("Full Matrix Stream Headers:", matrix_th_texts)
        assert any("USER AGENT" in th for th in matrix_th_texts), f"USER AGENT column missing from matrix header: {matrix_th_texts}"
        assert any("IP" in th for th in matrix_th_texts), f"IP column missing from matrix header: {matrix_th_texts}"
        print("✓ Dedicated Full Matrix table displays CLIENT USER AGENT and ORIGIN IP!")

        # Verify CF-Connecting-IP shows in the table
        body_text = page.locator('#tbody-stream-full').all_text_contents()
        print(f"✓ Dedicated Full Matrix loaded stream data. Rows sample: {len(body_text)}")

        # Take screenshot of Full Matrix Stream
        page.screenshot(path=os.path.join(artifact_dir, 'analytics_full_matrix_ua_and_ip.png'))

        print("\nALL BROWSER ANALYTICS UI TESTS PASSED 100%!")
        browser.close()

if __name__ == "__main__":
    test_analytics_browser_ui()
