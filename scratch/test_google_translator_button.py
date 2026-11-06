import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch browser with Asia/Dhaka timezone to simulate user in Bangladesh
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            timezone_id="Asia/Dhaka",
            locale="en-US",
            viewport={"width": 1440, "height": 900}
        )
        page = await context.new_page()

        print("Navigating to home page http://127.0.0.1:5000/ ...")
        await page.goto("http://127.0.0.1:5000/", wait_until="domcontentloaded")
        await page.wait_for_timeout(1000)

        # 1. Check if #global-lang-btn exists
        btn = page.locator("#global-lang-btn")
        is_visible = await btn.is_visible()
        print(f"Header Lang Button visible: {is_visible}")
        assert is_visible, "Language button should be visible in header!"

        btn_text = (await btn.inner_text()).strip()
        print(f"Initial button text: '{btn_text}'")
        assert "বাংলা" in btn_text or "BN" in btn_text or "TRANSLATE" in btn_text, f"Unexpected button text: {btn_text}"

        # 2. Check detection logic in browser context
        detected = await page.evaluate("window.NFLang && window.NFLang.detect()")
        print(f"Detected language for Asia/Dhaka: {detected}")
        assert detected == "bn", f"Expected detected language to be 'bn', got {detected}"

        # Take screenshot of clean initial state
        screenshot_dir = "/home/siuxsa/.gemini/antigravity-cli/brain/3c7d032f-a2e3-45fe-b45d-a0b246098d8b"
        await page.screenshot(path=os.path.join(screenshot_dir, "translate_btn_initial_state.png"))
        print("Captured translate_btn_initial_state.png")

        # 3. Click the translate button
        print("Clicking translate button...")
        await btn.click()
        await page.wait_for_timeout(1500)

        # Check googtrans cookie
        cookies = await context.cookies()
        googtrans = next((c for c in cookies if c['name'] == 'googtrans'), None)
        print(f"googtrans cookie: {googtrans}")
        assert googtrans is not None, "googtrans cookie should be set!"
        assert "/en/bn" in googtrans['value'], f"googtrans should contain /en/bn, got {googtrans['value']}"

        # Check button label updated to ENGLISH (EN)
        active_text = (await page.locator("#global-lang-btn").inner_text()).strip()
        print(f"Button text after activation: '{active_text}'")
        assert "ENGLISH" in active_text or "EN" in active_text, f"Button text should indicate restore to English, got: {active_text}"

        # Ensure no Google Translate banner pushed the body down
        body_top = await page.evaluate("window.getComputedStyle(document.body).top")
        print(f"Document body top: {body_top}")
        assert body_top in ("0px", "auto"), f"Body top margin should remain 0px, got {body_top}"

        # Capture screenshot of active translated state
        await page.screenshot(path=os.path.join(screenshot_dir, "translate_btn_active_state.png"))
        print("Captured translate_btn_active_state.png")

        # 4. Click again to restore English
        print("Clicking translate button again to restore English...")
        await page.locator("#global-lang-btn").click()
        await page.wait_for_timeout(1500)

        # Check cookies after reset
        cookies_after = await context.cookies()
        googtrans_after = next((c for c in cookies_after if c['name'] == 'googtrans' and '/en/bn' in c['value']), None)
        print(f"googtrans cookie after restore: {googtrans_after}")
        assert googtrans_after is None, "googtrans /en/bn should be cleared after restoring English!"

        print("ALL TESTS PASSED SUCCESSFULLY!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
