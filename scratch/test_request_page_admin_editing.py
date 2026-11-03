import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def test_request_page_admin_editing():
    print("=== TESTING CUSTOM TOOL REQUEST PAGE ADMIN EDITABILITY ===")

    session = requests.Session()
    # 1. Admin login
    login_resp = session.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"}, allow_redirects=True)
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.status_code}"
    print("✓ Master Admin authenticated successfully.")

    # 2. Check Admin Panel contains Request Page editing controls
    admin_resp = session.get(f"{BASE_URL}/admin")
    assert admin_resp.status_code == 200
    admin_html = admin_resp.text
    assert "CUSTOM TOOL REQUEST PAGE" in admin_html, "Expected '[05] CUSTOM TOOL REQUEST PAGE' tab in Text Studio"
    assert "theme-text-pane-request" in admin_html, "Expected '#theme-text-pane-request' pane in Text Studio"
    assert "REQUEST TOOL (/request)" in admin_html, "Expected Request Tool route buttons in Visual Canvas and SEO Studio"
    assert "seo-pane-request" in admin_html, "Expected '#seo-pane-request' pane in SEO Studio"
    print("✓ Admin panel successfully renders Request Page editing studios across Text, Visual, and SEO modules.")

    # 3. Test saving customized content for /request via POST /api/admin/theme
    custom_content = {
        "request_breadcrumb": "BESPOKE ARSENAL SOURCING",
        "request_eyebrow": "// RESTRICTED MISSION PROCUREMENT MATRIX",
        "request_title": "ACQUIRE CLASSIFIED CAPABILITIES.",
        "request_desc": "Bespoke exploit brokerage and zero-day acquisition protocol for nation-state red teams and tier-1 operators.",
        "request_form_eyebrow": "// CUSTOM MISSION SPECIFICATIONS",
        "request_form_title": "EXPLOIT MATRIX BRIEFING",
        "request_submit_btn": "TRANSMIT SOURCING BRIEF →",
        "request_security_badge": "MIL-SPEC TLS 1.3 & 4096-BIT PGP",
        "request_timeline_eyebrow": "// 3-PHASE BROKERAGE TIMELINE",
        "request_step1_title": "DEEP RECON & VERIFICATION",
        "request_step1_desc": "Target architecture validation within 120 minutes.",
        "request_step2_title": "ESCROW ALLOCATION",
        "request_step2_desc": "Multi-sig zero-knowledge deposit lock.",
        "request_step3_title": "DIRECT COURIER HANDOFF",
        "request_step3_desc": "Ephemeral one-time pad key delivery.",
        "request_concierge_eyebrow": "// DIRECT ESCROW DESK",
        "request_concierge_title": "DISPATCH CHIEF BROKER",
        "request_concierge_desc": "Immediate mission assistance available via high-security Telegram desk.",
        "request_concierge_btn": "CONNECT TO CHIEF BROKER →",
        "seo_request_title": "Bespoke Exploit Procurement | ZeroDay Matrix",
        "seo_request_desc": "Classified capabilities intake desk for exclusive zero-day procurement and bespoke payload engineering."
    }

    save_resp = session.post(f"{BASE_URL}/api/admin/theme", json=custom_content)
    assert save_resp.status_code == 200
    assert save_resp.json().get("ok") is True
    print("✓ Admin successfully saved custom content for Request Tool page.")

    # 4. Verify public /request renders the customized values live
    public_resp = requests.get(f"{BASE_URL}/request")
    assert public_resp.status_code == 200
    pub_html = public_resp.text

    assert "BESPOKE ARSENAL SOURCING" in pub_html
    assert "// RESTRICTED MISSION PROCUREMENT MATRIX" in pub_html
    assert "ACQUIRE CLASSIFIED CAPABILITIES." in pub_html
    assert "Bespoke exploit brokerage and zero-day acquisition protocol" in pub_html
    assert "// CUSTOM MISSION SPECIFICATIONS" in pub_html
    assert "EXPLOIT MATRIX BRIEFING" in pub_html
    assert "TRANSMIT SOURCING BRIEF →" in pub_html
    assert "MIL-SPEC TLS 1.3 &amp; 4096-BIT PGP" in pub_html or "MIL-SPEC TLS 1.3 & 4096-BIT PGP" in pub_html
    assert "DEEP RECON &amp; VERIFICATION" in pub_html or "DEEP RECON & VERIFICATION" in pub_html
    assert "Target architecture validation within 120 minutes." in pub_html
    assert "ESCROW ALLOCATION" in pub_html
    assert "DIRECT COURIER HANDOFF" in pub_html
    assert "DISPATCH CHIEF BROKER" in pub_html
    assert "CONNECT TO CHIEF BROKER →" in pub_html

    soup = BeautifulSoup(pub_html, "html.parser")
    title_tag = soup.find("title")
    assert "Bespoke Exploit Procurement" in title_tag.text
    meta_desc = soup.find("meta", attrs={"name": "description"})
    assert meta_desc and "Classified capabilities intake desk" in meta_desc.get("content", "")
    print("✓ Public /request accurately updated in real-time with customized copy and SEO metadata.")

    # 5. Restore default content cleanly
    defaults = {
        "request_breadcrumb": "CUSTOM SOURCING & TOOL PROCUREMENT",
        "request_eyebrow": "// PRIVATE SOURCING & EXPLOIT PROCUREMENT PROTOCOL",
        "request_title": "REQUEST UNLISTED TOOLS.",
        "request_desc": "Need an enterprise penetration suite, zero-day exploit module, reverse-engineering seat, or hardware implant not listed in our digital catalog? Submit your operational brief below.",
        "request_form_eyebrow": "// PROCUREMENT INTAKE SPECIFICATIONS",
        "request_form_title": "OPERATIONAL TOOL REQUIREMENTS",
        "request_submit_btn": "DISPATCH SOURCING REQUEST →",
        "request_security_badge": "PGP / TLS ENCRYPTED INTAKE",
        "request_timeline_eyebrow": "// SOURCING TIMELINE & PROTOCOL",
        "request_step1_title": "INTAKE & SCOPING",
        "request_step1_desc": "Our broker desk analyzes version requirements, build constraints, and vendor license compatibility within 4 hours.",
        "request_step2_title": "ALLOCATION & BENCHMARK",
        "request_step2_desc": "We secure perpetual enterprise seats, commercial licenses, or private zero-day proof-of-concepts from vetted brokers.",
        "request_step3_title": "TELEGRAM HANDOFF & VAULT",
        "request_step3_desc": "Cryptographic keys and deployment guides are transferred directly via our verified Telegram desk with escrow support.",
        "request_concierge_eyebrow": "// DIRECT PRIVATE BROKERAGE",
        "request_concierge_title": "TALK TO OUR SOURCING DESK",
        "request_concierge_desc": "For confidential high-value acquisitions ($25k+) or time-critical mission zero-days, message our lead procurement concierge directly on Telegram:",
        "request_concierge_btn": "TELEGRAM CONCIERGE DESK →",
        "seo_request_title": "",
        "seo_request_desc": ""
    }
    restore_resp = session.post(f"{BASE_URL}/api/admin/theme", json=defaults)
    assert restore_resp.status_code == 200
    print("✓ Successfully restored standard default settings.")

    print("\n=== ALL REQUEST PAGE ADMIN EDITABILITY TESTS PASSED 100%! ===")

if __name__ == "__main__":
    test_request_page_admin_editing()
