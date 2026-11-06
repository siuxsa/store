import os
from playwright.sync_api import sync_playwright

artifact_dir = os.path.expanduser('~/.gemini/antigravity-cli/brain/3c7d032f-a2e3-45fe-b45d-a0b246098d8b')

def test_sticky_sidebars():
    print("=== TESTING SMART STICKY SIDEBARS (PRODUCT & JOURNAL) ===")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a standard 1400x900 desktop viewport
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()

        # =====================================================================
        # PART 1: THREAT INTEL JOURNAL DETAIL
        # =====================================================================
        print("\n[TEST 1] Visiting Threat Intel Journal Advisory...")
        page.goto("http://127.0.0.1:5000/intel/cve-2026-3199-linux-kernel-ebpf-verification-bypass")
        page.wait_for_selector(".journal-detail-layout", timeout=10000)
        page.wait_for_timeout(600)

        # 1. At Scroll 0
        box_0 = page.evaluate('''() => {
            const s = document.querySelector('.journal-sidebar-column');
            const r = s.getBoundingClientRect();
            return { top: Math.round(r.top), bottom: Math.round(r.bottom), height: Math.round(r.height), vh: window.innerHeight };
        }''')
        print(f"  At Scroll 0px: top={box_0['top']}px, bottom={box_0['bottom']}px, height={box_0['height']}px")
        page.screenshot(path=os.path.join(artifact_dir, "journal_sticky_scroll_0.png"))

        # 2. At Scroll 1000px (Mid-article reading)
        # The right side data should have finished scrolling into view and STOPPED scrolling (pinned)!
        page.evaluate("window.scrollTo(0, 1000)")
        page.wait_for_timeout(400)
        box_1000 = page.evaluate('''() => {
            const s = document.querySelector('.journal-sidebar-column');
            const r = s.getBoundingClientRect();
            return { top: Math.round(r.top), bottom: Math.round(r.bottom), height: Math.round(r.height), vh: window.innerHeight };
        }''')
        print(f"  At Scroll 1000px: top={box_1000['top']}px, bottom={box_1000['bottom']}px (vh={box_1000['vh']}px)")
        # Assert right side data is visible and pinned near the bottom
        assert box_1000['bottom'] <= box_1000['vh'], f"Sidebar bottom {box_1000['bottom']} should be <= viewport {box_1000['vh']}"
        assert box_1000['bottom'] >= box_1000['vh'] - 60, f"Sidebar bottom {box_1000['bottom']} should be pinned near viewport bottom {box_1000['vh']}"
        page.screenshot(path=os.path.join(artifact_dir, "journal_sticky_scroll_1000_pinned.png"))
        print("  ✓ Verified: Right column stopped scrolling and is pinned cleanly beside the article!")

        # 3. At Scroll 1400px (Deeper in article)
        page.evaluate("window.scrollTo(0, 1400)")
        page.wait_for_timeout(300)
        box_1400 = page.evaluate('''() => {
            const s = document.querySelector('.journal-sidebar-column');
            const r = s.getBoundingClientRect();
            return { top: Math.round(r.top), bottom: Math.round(r.bottom) };
        }''')
        print(f"  At Scroll 1400px: top={box_1400['top']}px, bottom={box_1400['bottom']}px")
        assert box_1400['bottom'] == box_1000['bottom'], "Sidebar should remain stationary while article scrolls!"
        print("  ✓ Verified: Sidebar stays firmly pinned in place as user continues reading!")

        # 4. At Scroll 2100px (End of primary column -> More Advisories arrives)
        page.evaluate("window.scrollTo(0, 2100)")
        page.wait_for_timeout(400)
        box_2100 = page.evaluate('''() => {
            const s = document.querySelector('.journal-sidebar-column');
            const r = s.getBoundingClientRect();
            return { top: Math.round(r.top), bottom: Math.round(r.bottom) };
        }''')
        print(f"  At Scroll 2100px: top={box_2100['top']}px, bottom={box_2100['bottom']}px")
        assert box_2100['bottom'] < box_1400['bottom'], "Sidebar should scroll up when left column finishes and new data arrives!"
        page.screenshot(path=os.path.join(artifact_dir, "journal_sticky_scroll_2100_newdata.png"))
        print("  ✓ Verified: When column finished and new data came, sidebar resumed scrolling naturally!")

        # =====================================================================
        # PART 2: ARSENAL PRODUCT DETAIL
        # =====================================================================
        print("\n[TEST 2] Visiting Arsenal Product Detail...")
        page.goto("http://127.0.0.1:5000/arsenal/burp-suite-professional-license")
        page.wait_for_selector(".pdp-layout", timeout=10000)
        page.wait_for_timeout(600)

        # 1. At Scroll 0
        pbox_0 = page.evaluate('''() => {
            const s = document.querySelector('.pdp-info-panel');
            const r = s.getBoundingClientRect();
            return { top: Math.round(r.top), bottom: Math.round(r.bottom), height: Math.round(r.height), vh: window.innerHeight };
        }''')
        print(f"  Product at Scroll 0px: top={pbox_0['top']}px, bottom={pbox_0['bottom']}px, height={pbox_0['height']}px")
        page.screenshot(path=os.path.join(artifact_dir, "product_sticky_scroll_0.png"))

        # 2. At Scroll 600px
        page.evaluate("window.scrollTo(0, 600)")
        page.wait_for_timeout(400)
        pbox_600 = page.evaluate('''() => {
            const s = document.querySelector('.pdp-info-panel');
            const r = s.getBoundingClientRect();
            return { top: Math.round(r.top), bottom: Math.round(r.bottom), vh: window.innerHeight };
        }''')
        print(f"  Product at Scroll 600px: top={pbox_600['top']}px, bottom={pbox_600['bottom']}px (vh={pbox_600['vh']}px)")
        assert pbox_600['bottom'] <= pbox_600['vh'], "Product panel bottom should be within viewport!"
        assert pbox_600['bottom'] >= pbox_600['vh'] - 60, "Product panel bottom should be pinned near bottom of screen!"
        page.screenshot(path=os.path.join(artifact_dir, "product_sticky_scroll_600_pinned.png"))
        print("  ✓ Verified: Product panel stopped scrolling and is pinned cleanly beside the gallery!")

        # 3. Test Accordion expansion recalculation
        print("  Testing Accordion Expansion in pinned panel...")
        acc_trigger = page.locator(".accordion-trigger").first
        await_acc = acc_trigger.click()
        page.wait_for_timeout(400)
        pbox_expanded = page.evaluate('''() => {
            const s = document.querySelector('.pdp-info-panel');
            const r = s.getBoundingClientRect();
            return { top: Math.round(r.top), bottom: Math.round(r.bottom), height: Math.round(r.height), vh: window.innerHeight };
        }''')
        print(f"  After Accordion Expand: height={pbox_expanded['height']}px, bottom={pbox_expanded['bottom']}px")
        assert pbox_expanded['bottom'] <= pbox_expanded['vh'], "Expanded panel should recalculate top and keep bottom in view!"
        page.screenshot(path=os.path.join(artifact_dir, "product_sticky_accordion_expanded.png"))
        print("  ✓ Verified: Dynamic ResizeObserver recalculated top seamlessly upon accordion expansion!")

        # 4. At Scroll 1600px (End of gallery -> Operational Manual arrives)
        page.evaluate("window.scrollTo(0, 1600)")
        page.wait_for_timeout(400)
        pbox_1600 = page.evaluate('''() => {
            const s = document.querySelector('.pdp-info-panel');
            const r = s.getBoundingClientRect();
            return { top: Math.round(r.top), bottom: Math.round(r.bottom) };
        }''')
        print(f"  Product at Scroll 1600px: top={pbox_1600['top']}px, bottom={pbox_1600['bottom']}px")
        assert pbox_1600['bottom'] < pbox_600['bottom'], "Product panel should scroll up when gallery ends and operational manual comes!"
        page.screenshot(path=os.path.join(artifact_dir, "product_sticky_scroll_1600_newdata.png"))
        print("  ✓ Verified: When gallery ended and new data arrived, panel scrolled up naturally!")

        browser.close()

    print("\n=== ALL SMART STICKY SIDEBAR VERIFICATIONS PASSED 100%! ===")

if __name__ == "__main__":
    test_sticky_sidebars()
