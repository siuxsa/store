import os
from playwright.sync_api import sync_playwright

def test_topbar_and_settings():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        artifact_dir = '/home/siuxsa/.gemini/antigravity-cli/brain/3c7d032f-a2e3-45fe-b45d-a0b246098d8b'

        # ----------------------------------------------------
        # TEST 1: Topbar & Logout Button at 100% zoom (1280, 1024, 1366, 1440)
        # ----------------------------------------------------
        for width in [1280, 1024, 1366, 1440]:
            print(f"\n=== Testing Topbar at Width {width}px ===")
            context = browser.new_context(viewport={'width': width, 'height': 800})
            page = context.new_page()

            page.goto('http://127.0.0.1:5000/admin/login')
            page.fill('input[name="identifier"]', 'admin')
            page.fill('input[name="password"]', 'Admin@2026')
            page.click('button[type="submit"]')
            page.wait_for_url('**/admin')
            page.wait_for_timeout(800)

            logout = page.locator('a[href*="logout"]').bounding_box()
            topbar = page.locator('.admin-topbar').bounding_box()

            print(f"Viewport {width}px - Logout Box: {logout}")
            assert logout is not None, "Logout button not found!"
            logout_right = logout['x'] + logout['width']
            assert logout_right <= width, f"Logout button overflows! right edge: {logout_right} > {width}"
            assert logout['x'] >= 0, f"Logout button left edge negative: {logout['x']}"
            print(f"✓ Logout button is 100% safely inside UI at {width}px! (right edge: {logout_right:.1f}px <= {width}px)")

            if width == 1280:
                page.screenshot(path=os.path.join(artifact_dir, 'topbar_1280_logout_in_view.png'))
            context.close()

        # ----------------------------------------------------
        # TEST 2: Settings Subtabs Sticky Behavior
        # ----------------------------------------------------
        print("\n=== Testing Settings Sticky Subtabs ===")
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        page.goto('http://127.0.0.1:5000/admin/login')
        page.fill('input[name="identifier"]', 'admin')
        page.fill('input[name="password"]', 'Admin@2026')
        page.click('button[type="submit"]')
        page.wait_for_url('**/admin')
        page.wait_for_timeout(800)

        # Open System & Security -> Settings
        page.click('button[data-feature="system"]')
        page.wait_for_timeout(600)

        # Check Settings sticky panel presence
        settings_panel = page.locator('#mod-settings .settings-sticky-panel')
        assert settings_panel.count() == 1, "Settings sticky panel missing"

        initial_rect = settings_panel.bounding_box()
        print("Settings Panel Initial Y:", initial_rect['y'])

        # Scroll window down 500px
        page.evaluate("window.scrollTo(0, 500)")
        page.wait_for_timeout(500)

        scrolled_rect = settings_panel.bounding_box()
        print("Settings Panel Scrolled Y:", scrolled_rect['y'])
        assert abs(scrolled_rect['y'] - 112) < 2, f"Expected sticky panel at y=112, got {scrolled_rect['y']}"
        print("✓ Settings sticky panel stays pinned at top: 112px when scrolling!")

        # Verify subtabs are visible and interactable while scrolled down!
        tracking_btn = page.locator('#mod-settings .settings-subnav-btn[data-tab="tracking"]')
        assert tracking_btn.is_visible(), "Tracking subtab is not visible while scrolled down!"
        tracking_btn.click()
        page.wait_for_timeout(300)
        assert page.locator('#settings-pane-tracking').is_visible(), "Tracking pane did not open!"
        print("✓ Clicked TRACKING & JS subtab while scrolled down - opened successfully!")

        data_btn = page.locator('#mod-settings .settings-subnav-btn[data-tab="data"]')
        data_btn.click()
        page.wait_for_timeout(300)
        assert page.locator('#settings-pane-data').is_visible(), "Data ops pane did not open!"
        print("✓ Clicked DATA OPS subtab while scrolled down - opened successfully!")

        page.screenshot(path=os.path.join(artifact_dir, 'settings_scrolled_sticky_subtabs.png'))

        print("\nALL VERIFICATIONS PASSED 100%!")
        browser.close()

if __name__ == '__main__':
    test_topbar_and_settings()
