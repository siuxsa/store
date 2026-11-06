import asyncio
from playwright.async_api import async_playwright

async def test_locations():
    test_cases = [
        {"tz": "Europe/Paris", "locale": "fr-FR", "expected_code": "fr", "name": "French"},
        {"tz": "Europe/Berlin", "locale": "de-DE", "expected_code": "de", "name": "German"},
        {"tz": "Europe/Madrid", "locale": "es-ES", "expected_code": "es", "name": "Spanish"},
        {"tz": "Asia/Tokyo", "locale": "ja-JP", "expected_code": "ja", "name": "Japanese"},
        {"tz": "Asia/Dhaka", "locale": "en-US", "expected_code": "bn", "name": "Bangla via Dhaka Timezone"},
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for tc in test_cases:
            context = await browser.new_context(
                timezone_id=tc["tz"],
                locale=tc["locale"]
            )
            page = await context.new_page()
            await page.goto("http://127.0.0.1:5000/", wait_until="domcontentloaded")
            detected = await page.evaluate("window.NFLang && window.NFLang.detect()")
            print(f"[{tc['name']}] TZ: {tc['tz']} Locale: {tc['locale']} -> Detected: {detected} (Expected: {tc['expected_code']})")
            assert detected == tc["expected_code"], f"Failed for {tc['name']}"
            await context.close()
        await browser.close()
        print("ALL INTERNATIONAL LOCATION DETECTIONS VERIFIED!")

if __name__ == "__main__":
    asyncio.run(test_locations())
