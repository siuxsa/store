import os
import sys
import time
from playwright.sync_api import sync_playwright

artifact_dir = os.path.expanduser('~/.gemini/antigravity-cli/brain/3c7d032f-a2e3-45fe-b45d-a0b246098d8b')

def run_tests():
    native_dialogs_caught = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()

        # Listen for any native dialogs - NONE should ever fire!
        page.on("dialog", lambda dialog: native_dialogs_caught.append({
            "type": dialog.type,
            "message": dialog.message
        }))

        # Step 1: Login as admin
        print("[TEST] 1. Authenticating at /admin/login...")
        page.goto("http://127.0.0.1:5000/admin/login")
        page.fill('input[name="identifier"]', "admin")
        page.fill('input[name="password"]', "Admin@2026")
        page.click('button[type="submit"]')
        page.wait_for_selector("#mod-analytics", timeout=10000)
        print("  ✓ Authenticated into Admin Dashboard.")

        # Step 2: Test Product Studio template confirm modal
        print("[TEST] 2. Testing Product Studio Template Confirmation Modal...")
        page.evaluate("""() => {
            if (typeof switchAdminTab === 'function') switchAdminTab('product-editor', null);
            if (typeof switchProductStudioTab === 'function') switchProductStudioTab('manual', null);
            const ta = document.getElementById('pse-description');
            if (ta) ta.value = 'Custom manual operator specifications draft that must be protected.';
        }""")
        page.wait_for_timeout(400)

        # Trigger template load asynchronously so evaluate doesn't wait for user click
        page.evaluate("() => { setTimeout(() => loadProductMarkdownTemplate('arch'), 0); }")
        page.wait_for_timeout(400)

        # Check that #modal-confirm is open
        confirm_modal = page.locator("#modal-confirm")
        assert confirm_modal.is_visible(), "Expected #modal-confirm to be visible!"
        title = page.locator("#confirm-modal-title").text_content()
        print("  ✓ Confirm modal appeared with title:", title)
        assert "LOAD SYSTEM TEMPLATE" in title or "TEMPLATE" in title

        # Take screenshot of Product Studio template confirm modal
        page.screenshot(path=os.path.join(artifact_dir, "modal_product_template_confirm.png"))
        print("  ✓ Saved screenshot: modal_product_template_confirm.png")

        # Click Cancel first to verify it cancels without overwriting
        page.locator("#confirm-modal-cancel-btn").click()
        page.wait_for_timeout(300)
        assert not confirm_modal.is_visible(), "Modal should be closed after cancel!"
        val = page.evaluate("() => document.getElementById('pse-description').value")
        assert "Custom manual operator" in val, "Draft was prematurely overwritten!"
        print("  ✓ Cancel preserved user draft perfectly.")

        # Click again and confirm replacement
        page.evaluate("() => { setTimeout(() => loadProductMarkdownTemplate('arch'), 0); }")
        page.wait_for_timeout(400)
        page.locator("#confirm-modal-ok-btn").click()
        page.wait_for_timeout(400)
        val = page.evaluate("() => document.getElementById('pse-description').value")
        assert "SYSTEM ARCHITECTURE" in val, "Template was not loaded after confirmation!"
        print("  ✓ Confirm replaced draft with structured template.")

        # Step 3: Test Post Studio custom prompt modal (Hyperlink insertion)
        print("[TEST] 3. Testing Post Studio Prompt Modal (Hyperlink / Image insertion)...")
        page.evaluate("""() => {
            if (typeof switchAdminTab === 'function') switchAdminTab('post-editor', null);
            if (typeof switchPostStudioTab === 'function') switchPostStudioTab('markdown', null);
        }""")
        page.wait_for_timeout(400)

        # Trigger prompt modal via window.showPromptModal
        page.evaluate("""() => {
            window.showPromptModal({
                title: 'INSERT HYPERLINK',
                message: 'Enter target destination URL for the highlighted anchor text:',
                defaultValue: 'https://security.matrix.test',
                placeholder: 'https://example.com'
            }).then(val => { window._testPromptVal = val; });
        }""")

        page.wait_for_timeout(300)
        assert confirm_modal.is_visible(), "Expected prompt modal to be visible!"
        input_el = page.locator("#confirm-modal-input")
        assert input_el.is_visible(), "Expected prompt input box to be visible!"
        input_val = input_el.input_value()
        print("  ✓ Prompt modal appeared with prefilled value:", input_val)

        # Take screenshot of Prompt Modal
        page.screenshot(path=os.path.join(artifact_dir, "modal_prompt_input_verified.png"))
        print("  ✓ Saved screenshot: modal_prompt_input_verified.png")

        # Fill input and click OK
        input_el.fill("https://cve-database.mitre.org/vuln-2026")
        page.locator("#confirm-modal-ok-btn").click()
        page.wait_for_timeout(300)
        prompt_res = page.evaluate("() => window._testPromptVal")
        assert prompt_res == "https://cve-database.mitre.org/vuln-2026", f"Prompt result mismatch: {prompt_res}"
        print("  ✓ Prompt resolved with custom user input:", prompt_res)

        # Step 4: Test Theme Studio Revert Modal
        print("[TEST] 4. Testing Theme Studio Revert Modal...")
        page.evaluate("""() => {
            if (typeof switchAdminTab === 'function') switchAdminTab('themes-visual', null);
        }""")
        page.wait_for_timeout(400)
        page.evaluate("() => { setTimeout(() => resetThemeStudio(), 0); }")
        page.wait_for_timeout(400)
        assert confirm_modal.is_visible(), "Expected Theme Studio revert modal to be visible!"
        theme_title = page.locator("#confirm-modal-title").text_content()
        print("  ✓ Theme Revert Modal title:", theme_title)
        assert "REVERT THEME STUDIO" in theme_title
        page.locator("#confirm-modal-cancel-btn").click()
        page.wait_for_timeout(300)
        print("  ✓ Theme Studio Revert cancelled cleanly.")

        # Step 5: Test Operator Vault Token Regeneration on Storefront (/vault)
        print("[TEST] 5. Testing Operator Vault Token Regeneration Modal on Storefront (/vault)...")
        # Open a new clean context for the client operator
        client_context = browser.new_context(viewport={"width": 1400, "height": 900})
        client_page = client_context.new_page()
        client_page.on("dialog", lambda dialog: native_dialogs_caught.append({
            "type": dialog.type,
            "message": dialog.message
        }))

        # Login as customer operator
        client_page.goto("http://127.0.0.1:5000/login")
        client_page.fill('input[name="identifier"]', "redteam_operator")
        client_page.fill('input[name="password"]', "Operator@2026")
        client_page.click('button[type="submit"]')
        client_page.wait_for_selector("#vault-api-token", timeout=10000)
        old_token = client_page.locator("#vault-api-token").text_content()
        print("  Current token in vault:", old_token.strip())

        # Click the Regenerate button
        regen_btn = client_page.locator('button:has-text("REGENERATE")')
        regen_btn.click()
        client_page.wait_for_timeout(400)

        # Confirm modal should appear on /vault!
        vault_confirm = client_page.locator("#modal-confirm")
        assert vault_confirm.is_visible(), "Expected #modal-confirm to appear in Operator Vault!"
        vault_modal_title = client_page.locator("#confirm-modal-title").text_content()
        print("  ✓ Vault Modal Title:", vault_modal_title)
        assert "REGENERATE" in vault_modal_title

        # Take screenshot of Vault Confirm Modal
        client_page.screenshot(path=os.path.join(artifact_dir, "modal_vault_token_confirm.png"))
        print("  ✓ Saved screenshot: modal_vault_token_confirm.png")

        # Click OK to regenerate
        client_page.locator("#confirm-modal-ok-btn").click()
        client_page.wait_for_timeout(1000)

        # Check for toast notification and new token
        new_token = client_page.locator("#vault-api-token").text_content()
        print("  New token in vault:", new_token.strip())
        assert new_token.strip() != old_token.strip(), "Token was not updated!"

        toast = client_page.locator("#global-toast-container")
        assert toast.is_visible(), "Expected toast notification to appear!"
        toast_text = toast.text_content()
        print("  ✓ Toast notification verified:", toast_text)

        # Take screenshot of toast notification in Vault
        client_page.screenshot(path=os.path.join(artifact_dir, "vault_toast_success_verified.png"))
        print("  ✓ Saved screenshot: vault_toast_success_verified.png")

        # Step 6: Verify Zero Native Dialogs Fired Throughout Whole Run
        print("[TEST] 6. Verifying zero native browser dialogs were triggered...")
        print("  Native dialogs intercepted by Chrome/Playwright:", native_dialogs_caught)
        assert len(native_dialogs_caught) == 0, f"FAIL: Native dialogs were triggered! {native_dialogs_caught}"
        print("  ✓ 100% SUCCESS: ZERO native popups appeared across entire test execution!")

        browser.close()

if __name__ == "__main__":
    run_tests()
