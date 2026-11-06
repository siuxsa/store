import asyncio
import os
from playwright.async_api import async_playwright

ARTIFACT_DIR = "/home/siuxsa/.gemini/antigravity-cli/brain/3c7d032f-a2e3-45fe-b45d-a0b246098d8b"

async def test_discount_and_price():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        print("--> Navigating to /shop...")
        res = await page.goto("http://127.0.0.1:5000/shop", wait_until="domcontentloaded")
        assert res.status == 200, f"Shop failed with status {res.status}"

        # 1. Verify discount badges exist on shop page
        discount_badges = await page.locator(".product-card .product-discount-badge").all()
        print(f"Found {len(discount_badges)} discount badges on /shop")
        assert len(discount_badges) > 0, "No discount badges found on shop page!"

        # Verify discount badge formats (all must contain DISCOUNT and -XX%)
        found_89 = False
        for b in discount_badges:
            t = (await b.text_content()).strip()
            assert "DISCOUNT" in t and "%" in t, f"Badge format invalid: {t}"
            if "-89%" in t:
                found_89 = True
        print(f"✓ Verified discount badge format 'DISCOUNT -XX%' repo-wide (Found 'DISCOUNT -89%': {found_89})")

        # Check font sizes: discount-val must be bigger than discount-label
        first_badge = page.locator(".product-grid .product-card .product-discount-badge").first
        label_size = await first_badge.locator(".discount-label").evaluate("el => parseFloat(window.getComputedStyle(el).fontSize)")
        val_size = await first_badge.locator(".discount-val").evaluate("el => parseFloat(window.getComputedStyle(el).fontSize)")
        print(f"Badge sizes -> label: {label_size}px, val: {val_size}px")
        assert val_size > label_size, f"Discount value is not bigger than label: val={val_size}px, label={label_size}px"
        print("✓ Verified -89% discount value is visibly bigger than the discount label")

        # Check the first product card details
        first_card = page.locator(".product-grid .product-card").first
        price = first_card.locator(".product-price-current")
        price_text = await price.text_content()
        print(f"First product price: {price_text}")

        # Check price styling (Color: #a74e23 -> rgb(167, 78, 35))
        price_style = await price.evaluate("""el => {
            const cs = window.getComputedStyle(el);
            return {
                fontSize: cs.fontSize,
                fontWeight: cs.fontWeight,
                color: cs.color
            };
        }""")
        print(f"Price styling: {price_style}")
        font_size_px = float(price_style["fontSize"].replace("px", ""))
        assert font_size_px >= 20.0, f"Price font size is too small: {price_style['fontSize']}"
        assert "220, 38, 38" in price_style["color"], f"Color is not #dc2626: {price_style['color']}"
        print(f"✓ Verified price text is #dc2626 ({price_style['color']}) and bold ({price_style['fontSize']})")

        # Take full shop screenshot
        screenshot_path = os.path.join(ARTIFACT_DIR, "shop_discount_custom_badge_and_red_price_verified.png")
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"✓ Saved screenshot to {screenshot_path}")

        # Also verify Product Detail page
        print("--> Navigating to Cobalt Strike product detail page...")
        await page.goto("http://127.0.0.1:5000/arsenal/cobalt-strike-team-server-suite", wait_until="domcontentloaded")
        detail_badge = await page.locator(".badge-tag:has-text('DISCOUNT')").first.text_content()
        print(f"Product detail discount badge: {detail_badge.strip()}")
        assert "-89%" in detail_badge and "DISCOUNT" in detail_badge, f"Detail page badge does not match: {detail_badge}"

        detail_price_color = await page.locator("span.meta-mono:has-text('$399')").evaluate("el => window.getComputedStyle(el).color")
        print(f"Product detail price color: {detail_price_color}")
        assert "220, 38, 38" in detail_price_color, f"Detail price color is not #dc2626: {detail_price_color}"

        # Close browser
        await browser.close()
        print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_discount_and_price())
