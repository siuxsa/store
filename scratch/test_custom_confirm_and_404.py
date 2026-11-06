import os
from playwright.sync_api import sync_playwright

def test_custom_confirm_and_404():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        artifact_dir = '/home/siuxsa/.gemini/antigravity-cli/brain/3c7d032f-a2e3-45fe-b45d-a0b246098d8b'

        # Login to admin
        page.goto('http://127.0.0.1:5000/admin/login')
        page.fill('input[name="identifier"]', 'admin')
        page.fill('input[name="password"]', 'Admin@2026')
        page.click('button[type="submit"]')
        page.wait_for_url('**/admin')
        page.wait_for_timeout(800)

        # ----------------------------------------------------
        # TEST 1: Custom Confirmation Popup Modal
        # ----------------------------------------------------
        print("=== TEST 1: Testing Custom Cyberpunk Confirmation Modal ===")
        # Trigger showConfirmModal via page.evaluate
        page.evaluate("""() => {
            window._testConfirmResult = null;
            window.showConfirmModal({
                title: 'PURGE ARSENAL SYSTEM',
                message: 'Are you sure you want to permanently delete "BURP-SUITE-ENTERPRISE-2026"?',
                confirmText: 'DELETE SYSTEM',
                note: 'WARNING: Digital license configurations and cryptographic checksums will be erased.'
            }).then(res => { window._testConfirmResult = res; });
        }""")
        page.wait_for_timeout(400)

        # Assert modal is visible
        modal = page.locator('#modal-confirm')
        assert modal.is_visible(), "Custom confirm modal did not open!"
        assert "PURGE ARSENAL SYSTEM" in page.locator('#confirm-modal-title').text_content()
        assert "DELETE SYSTEM" in page.locator('#confirm-modal-ok-text').text_content()
        print("✓ Custom confirmation modal is open with custom cyberpunk styling and texts!")

        # Take screenshot of the custom popup
        page.screenshot(path=os.path.join(artifact_dir, 'custom_confirm_modal.png'))

        # Click cancel
        page.click('#confirm-modal-cancel-btn')
        page.wait_for_timeout(300)
        assert not modal.is_visible(), "Modal should be closed after Cancel"
        res_cancel = page.evaluate("() => window._testConfirmResult")
        assert res_cancel is False, f"Expected False on cancel, got {res_cancel}"
        print("✓ Cancel button cleanly dismisses modal and returns false.")

        # Test Confirm button
        page.evaluate("""() => {
            window._testConfirmResult = null;
            window.showConfirmModal({
                title: 'PERMANENT DELETION',
                message: 'Confirm deletion?',
                confirmText: 'CONFIRM & EXECUTE'
            }).then(res => { window._testConfirmResult = res; });
        }""")
        page.wait_for_timeout(300)
        page.click('#confirm-modal-ok-btn')
        page.wait_for_timeout(300)
        res_ok = page.evaluate("() => window._testConfirmResult")
        assert res_ok is True, f"Expected True on confirm, got {res_ok}"
        print("✓ Confirm button cleanly executes action and returns true.")

        # ----------------------------------------------------
        # TEST 2: 404 in Text-Based Content Studio & Visual Inspect Studio
        # ----------------------------------------------------
        print("\n=== TEST 2: Testing 404 Text Studio & Visual Inspect Studio ===")
        # 1. Verify 404 is NOT in Settings tab
        page.click('button[data-feature="system"]')
        page.wait_for_timeout(400)
        subtab_404_settings = page.locator('.settings-subnav-btn[data-tab="error404"]')
        assert not subtab_404_settings.is_visible(), "404 should NOT be in Settings tab! It belongs in Themes Visual & Text studios."
        print("✓ Confirmed: 404 is cleanly removed from Settings module.")

        # 2. Switch to Text-Based Theme & Content Studio
        page.evaluate("() => switchFeature('system', 'themes-text')")
        page.wait_for_timeout(400)
        assert page.locator('#mod-themes-text').is_visible(), "Text theme studio module did not open!"

        # Click the 404 PAGE subnav button in Text Studio
        subtab_404_text = page.locator('.theme-text-subnav-btn:has-text("404 PAGE")')
        assert subtab_404_text.is_visible(), "404 PAGE subnav button missing in Text Theme Studio!"
        subtab_404_text.click()
        page.wait_for_timeout(300)

        pane_404_text = page.locator('#theme-text-pane-404')
        assert pane_404_text.is_visible(), "404 pane in Text Theme Studio did not open!"
        print("✓ 404 PAGE subtab in Text Theme Studio is active and visible.")

        # Fill in custom 404 values in Text Studio
        badge_input = page.locator('#theme-text-pane-404 input[name="error_404_badge"]')
        badge_input.fill('TACTICAL ANOMALY // 0x404_BREACH')
        badge_input.dispatch_event('input')

        title_input = page.locator('#theme-text-pane-404 input[name="error_404_title"]')
        title_input.fill('404 // AIRGAP_RESTRICTED')
        title_input.dispatch_event('input')

        headline_input = page.locator('#theme-text-pane-404 input[name="error_404_headline"]')
        headline_input.fill('SECTOR IS ISOLATED OR DECOMMISSIONED')
        headline_input.dispatch_event('input')

        msg_input = page.locator('#theme-text-pane-404 textarea[name="error_404_message"]')
        msg_input.fill('Access to this tactical node has been terminated by master security protocol.')
        msg_input.dispatch_event('input')

        # Take screenshot of Text Theme Studio with 404 pane
        page.screenshot(path=os.path.join(artifact_dir, 'admin_404_text_studio.png'))

        # Save via Text Theme Studio
        page.click('#btn-save-theme-text')
        page.wait_for_timeout(1000)
        print("✓ Saved custom 404 copywriting via Text Theme Studio.")

        # 3. Test Visual Inspect Studio with 404 Canvas Page
        page.evaluate("() => switchFeature('system', 'themes-visual')")
        page.wait_for_timeout(400)
        assert page.locator('#mod-themes-visual').is_visible(), "Visual Inspect Studio did not open!"

        # Click 404 PAGE in the Visual Canvas switcher strip
        btn_404_visual = page.locator('#mod-themes-visual .subnav-btn:has-text("404 PAGE")')
        assert btn_404_visual.is_visible(), "404 PAGE button missing in Visual Inspect switcher strip!"
        btn_404_visual.click()
        page.wait_for_timeout(800)

        url_label = page.locator('#theme-preview-url-label').text_content()
        assert '404' in url_label, f"URL label did not switch to 404: {url_label}"
        print("✓ Visual Inspect Studio switched to 404 live canvas (/404-preview-live).")

        # Test point-and-click inspect on the 404 page in the visual canvas
        iframe = page.frame_locator('#theme-preview-iframe')
        title_el = iframe.locator('[data-theme-bind="error_404_title"]')
        assert title_el.is_visible(), "404 title element missing in iframe!"
        page.evaluate("() => { if (!window.THEME_INSPECT_MODE) toggleInspectMode(); }")
        page.wait_for_timeout(300)
        title_el.click()
        page.wait_for_timeout(500)
        modal = page.locator('#modal-theme-element')
        assert modal.is_visible(), "Quick edit modal did not open on 404 title click!"
        assert page.locator('#quick-edit-field-key').input_value() == 'error_404_title'
        print("✓ Point-and-click inspection works on 404 canvas elements!")
        page.evaluate("() => closeModal('modal-theme-element')")
        page.wait_for_timeout(300)

        # Take screenshot of Visual Inspect Studio with 404 Canvas
        page.screenshot(path=os.path.join(artifact_dir, 'admin_404_visual_studio.png'))

        # ----------------------------------------------------
        # TEST 3: Visit 404 in public storefront
        # ----------------------------------------------------
        print("\n=== TEST 3: Verifying Public 404 Page with Saved Settings ===")
        context2 = browser.new_context(viewport={'width': 1280, 'height': 800})
        page2 = context2.new_page()

        resp = page2.goto('http://127.0.0.1:5000/random-dead-link-to-trigger-404')
        assert resp.status == 404, f"Expected HTTP 404, got {resp.status}"

        # Verify edited values show on the public 404 page!
        content = page2.content()
        assert 'TACTICAL ANOMALY // 0x404_BREACH' in content, "Saved badge missing from 404 page!"
        assert '404 // AIRGAP_RESTRICTED' in content, "Saved title missing from 404 page!"
        assert 'SECTOR IS ISOLATED OR DECOMMISSIONED' in content, "Saved headline missing from 404 page!"
        assert 'Access to this tactical node has been terminated' in content, "Saved message missing from 404 page!"
        print("✓ Public 404 page rendered the custom edited values from Text Studio perfectly!")

        page2.screenshot(path=os.path.join(artifact_dir, 'public_404_page_verified.png'))

        print("\nALL VERIFICATIONS PASSED 100%!")
        browser.close()

if __name__ == '__main__':
    test_custom_confirm_and_404()
