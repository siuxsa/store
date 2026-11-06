import asyncio
import os
from playwright.async_api import async_playwright

ARTIFACT_DIR = "/home/siuxsa/.gemini/antigravity-cli/brain/3c7d032f-a2e3-45fe-b45d-a0b246098d8b"

async def test_share_modal():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},
            permissions=["clipboard-read", "clipboard-write"]
        )
        page = await context.new_page()

        await page.add_init_script("""
            window._openedWindows = [];
            window.open = function(url, target, features) {
                window._openedWindows.push({ url: url, target: target, features: features });
                return { focus: function() {}, close: function() {} };
            };
        """)

        advisory_url = "http://127.0.0.1:5000/intel/cve-2026-8841-oauth2-token-smuggling-cloud-gateways"
        print(f"--> Navigating to {advisory_url}...")
        res = await page.goto(advisory_url, wait_until="domcontentloaded")
        assert res.status == 200, f"Page load failed: {res.status}"

        # 1. Check SHARE ADVISORY button exists and click
        share_btn = page.locator("#share-advisory-btn")
        await share_btn.wait_for(state="visible")
        print("--> Clicking 'SHARE ADVISORY' button...")
        await share_btn.click()

        # 2. Check Minimal Modal is visible
        modal = page.locator("#modal-share-advisory")
        await modal.wait_for(state="visible")
        is_open = await modal.evaluate("el => el.classList.contains('is-open') && window.getComputedStyle(el).display === 'flex'")
        assert is_open, "Modal is not open or display is not flex!"
        print("✓ Verified Share Modal popped up")

        # 3. Check clean brand styling (white background, #a74e23 close hover, no cluttered text)
        card = page.locator(".share-modal-card")
        card_bg = await card.evaluate("el => window.getComputedStyle(el).backgroundColor")
        print(f"Card background color: {card_bg}")
        assert "255, 255, 255" in card_bg, f"Expected clean white card background, got: {card_bg}"

        heading = (await page.locator("#share-modal-heading").text_content()).strip()
        print(f"Modal heading: {heading}")
        assert heading == "SHARE ADVISORY", f"Unexpected heading: {heading}"

        # Verify no unnecessary text like 'TELEMETRY BROADCAST' or 'PGP SIGNED' exists in the modal
        modal_all_text = await modal.text_content()
        assert "TELEMETRY" not in modal_all_text, "Found unnecessary telemetry text!"
        assert "PGP" not in modal_all_text, "Found unnecessary PGP text!"
        print("✓ Verified ZERO unnecessary text clutter in the modal")

        # 4. Check All 4 Share Channels Exist (Facebook, X, Gmail, Copy)
        fb_btn = page.locator("#share-btn-fb")
        x_btn = page.locator("#share-btn-x")
        gmail_btn = page.locator("#share-btn-gmail")
        copy_btn = page.locator("#share-btn-copy")

        assert await fb_btn.is_visible(), "Facebook button not visible"
        assert await x_btn.is_visible(), "X button not visible"
        assert await gmail_btn.is_visible(), "Gmail button not visible"
        assert await copy_btn.is_visible(), "Copy button not visible"
        print("✓ Verified all 4 share icons are visible (Facebook, X, Gmail, Copy)")

        # Save screenshot of opened minimal brand modal
        modal_screenshot = os.path.join(ARTIFACT_DIR, "share_advisory_minimal_brand_opened.png")
        await page.screenshot(path=modal_screenshot, full_page=False)
        print(f"✓ Saved minimal brand modal screenshot to {modal_screenshot}")

        # 5. Test Social Redirections
        # Facebook
        await fb_btn.click()
        opened = await page.evaluate("() => window._openedWindows")
        assert len(opened) == 1
        assert "facebook.com/sharer/sharer.php" in opened[0]["url"]
        assert "cve-2026-8841" in opened[0]["url"]
        print(f"✓ Verified Facebook redirect: {opened[0]['url']}")

        # X
        await x_btn.click()
        opened = await page.evaluate("() => window._openedWindows")
        assert len(opened) == 2
        assert "twitter.com/intent/tweet" in opened[1]["url"]
        assert "cve-2026-8841" in opened[1]["url"]
        print(f"✓ Verified X redirect: {opened[1]['url']}")

        # Gmail
        await gmail_btn.click()
        opened = await page.evaluate("() => window._openedWindows")
        assert len(opened) == 3
        assert "mail.google.com/mail" in opened[2]["url"]
        assert "cve-2026-8841" in opened[2]["url"]
        print(f"✓ Verified Gmail redirect: {opened[2]['url']}")

        # 6. Test Copy URL Button
        print("--> Testing Copy button...")
        await copy_btn.click()
        await page.wait_for_timeout(300)

        # Check Toast appeared
        toast = page.locator("#global-toast-container")
        await toast.wait_for(state="visible")
        toast_text = await toast.text_content()
        print(f"Toast message: {toast_text}")
        assert "copied" in toast_text.lower(), f"Expected copy toast notification, got: {toast_text}"

        # Check Copy label updated to Copied!
        copy_label = await page.locator("#share-copy-label").text_content()
        print(f"Copy label: {copy_label}")
        assert "copied" in copy_label.lower()

        # Save screenshot of copied state
        copied_screenshot = os.path.join(ARTIFACT_DIR, "share_advisory_minimal_brand_copied.png")
        await page.screenshot(path=copied_screenshot, full_page=False)
        print(f"✓ Saved copied state screenshot to {copied_screenshot}")

        # 7. Test Close Modal
        close_btn = page.locator("#share-modal-close-x")
        await close_btn.click()
        await page.wait_for_timeout(200)
        is_closed = await modal.evaluate("el => window.getComputedStyle(el).display === 'none'")
        assert is_closed, "Modal did not close on clicking X"
        print("✓ Verified Modal closed cleanly")

        await browser.close()
        print("=== ALL MINIMAL BRAND SHARE ADVISORY TESTS PASSED 100%! ===")

if __name__ == "__main__":
    asyncio.run(test_share_modal())
