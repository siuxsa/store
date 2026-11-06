import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            timezone_id="Asia/Dhaka",
            locale="en-US",
            viewport={"width": 1440, "height": 900}
        )
        page = await context.new_page()
        await page.goto("http://127.0.0.1:5000/", wait_until="domcontentloaded")
        await page.wait_for_timeout(600)

        header = page.locator("#site-header")
        screenshot_dir = "/home/siuxsa/.gemini/antigravity-cli/brain/3c7d032f-a2e3-45fe-b45d-a0b246098d8b"
        await header.screenshot(path=os.path.join(screenshot_dir, "header_professional_translate_icon.png"))
        print("Captured header_professional_translate_icon.png")

        # Hover state
        btn = page.locator("#global-lang-btn")
        await btn.hover()
        await page.wait_for_timeout(300)
        await header.screenshot(path=os.path.join(screenshot_dir, "header_professional_translate_hover.png"))
        print("Captured header_professional_translate_hover.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
