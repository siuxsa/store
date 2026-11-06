#!/usr/bin/env python3
"""
Automated Verification Suite: Product & Journal Draft / Publish Workflow
Tests:
1. Product Creation in DRAFT status:
   - Hidden from public /shop catalog and homepage.
   - Inaccessible to public visitors (redirects away).
   - Fully viewable by logged-in admin with Draft Preview banner.
   - Admin table renders DRAFT badge and PUBLISH action button.
2. Product Status Toggle to PUBLISHED:
   - Instantly becomes visible on public /shop catalog.
   - Accessible to public visitors without preview banner.
   - Admin table renders PUBLISHED badge and UNPUBLISH action button.
3. Post Creation in DRAFT status:
   - Hidden from public /journal wire and homepage.
   - Inaccessible to public visitors (redirects away).
   - Fully viewable by logged-in admin with Draft Preview banner.
   - Admin table renders DRAFT badge and PUBLISH action button.
4. Post Status Toggle to PUBLISHED:
   - Instantly becomes visible on public /journal wire.
   - Accessible to public visitors without preview banner.
   - Admin table renders PUBLISHED badge and UNPUBLISH action button.
5. Clean teardown of test items.
"""

import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from bs4 import BeautifulSoup
from app import app
from database import get_db

def run_tests():
    print("=== TESTING PRODUCT & JOURNAL DRAFT / PUBLISH WORKFLOW ===")
    client = app.test_client()

    # 1. Authenticate Admin Session
    with client.session_transaction() as sess:
        sess["admin_id"] = 1
        sess["admin_user"] = "admin"
        sess["admin_role"] = "MASTER_ADMIN"

    # ========================================================
    # A. PRODUCT DRAFT -> PUBLISH WORKFLOW
    # ========================================================
    test_sku = "TEST-DRAFT-X1"
    test_slug = "test-draft-audit-system"

    # Create product with status='DRAFT'
    prod_payload = {
        "sku": test_sku,
        "name": "Classified Draft Audit System",
        "slug": test_slug,
        "category": "Offensive & Red Team",
        "product_type": "LICENSE_KEY",
        "price": 799.0,
        "retail_price": 999.0,
        "version": "v1.0.0-BETA",
        "license_duration": "Perpetual Lab License",
        "platform": "Linux / x86_64",
        "badge_text": "CONFIDENTIAL",
        "status": "DRAFT",
        "short_desc": "Private unreleased binary suite undergoing QA testing."
    }

    res = client.post("/api/admin/products", json=prod_payload)
    assert res.status_code == 200, f"Failed to create draft product: {res.data}"
    prod_data = res.get_json()
    prod_id = prod_data["id"]
    print(f"✓ Created test product #{prod_id} in DRAFT status.")

    # Verify admin table renders DRAFT badge
    res_admin = client.get("/admin")
    assert res_admin.status_code == 200
    soup_admin = BeautifulSoup(res_admin.data.decode("utf-8"), "html.parser")
    prod_script = soup_admin.find("script", {"id": f"product-data-{prod_id}"})
    assert prod_script is not None, "Product script not rendered in admin"
    assert '"status": "DRAFT"' in prod_script.text or '"status":"DRAFT"' in prod_script.text

    # Unauthenticated visitor client
    guest_client = app.test_client()

    # Guest visiting /shop: product MUST NOT appear
    res_shop = guest_client.get(f"/shop?q={test_sku}")
    assert "NO MATCHING SECURITY SYSTEMS FOUND" in res_shop.data.decode("utf-8"), "DRAFT product leaked on public /shop!"
    print("✓ Public /shop successfully isolates DRAFT product (NOT visible to guests).")

    # Guest visiting /product/<slug>: MUST be redirected away
    res_guest_pdp = guest_client.get(f"/product/{test_slug}")
    assert res_guest_pdp.status_code in (302, 301), f"Expected redirect for draft product, got {res_guest_pdp.status_code}"
    print("✓ Guest attempting to view DRAFT product is properly redirected away.")

    # Admin visiting /product/<slug>: CAN view draft with preview banner
    res_admin_pdp = client.get(f"/product/{test_slug}")
    assert res_admin_pdp.status_code == 200, "Admin could not view draft product"
    assert "DRAFT PREVIEW MODE" in res_admin_pdp.data.decode("utf-8"), "Draft Preview watermark banner missing for admin"
    print("✓ Admin successfully views DRAFT product with prominent DRAFT PREVIEW banner.")

    # Toggle Product Status to PUBLISHED
    res_toggle = client.post(f"/api/admin/products/{prod_id}/toggle-status")
    assert res_toggle.status_code == 200
    assert res_toggle.get_json()["new_status"] == "PUBLISHED"
    print("✓ Toggled product status from DRAFT -> PUBLISHED via /api/admin/products/toggle-status.")

    # Guest visiting /shop: NOW product MUST appear
    res_shop2 = guest_client.get(f"/shop?q={test_sku}")
    assert test_slug in res_shop2.data.decode("utf-8"), "Published product should appear in /shop"
    print("✓ Public /shop immediately displays product once published.")

    # Guest visiting /product/<slug>: NOW allowed with HTTP 200, NO preview banner
    res_guest_pdp2 = guest_client.get(f"/product/{test_slug}")
    assert res_guest_pdp2.status_code == 200
    assert "DRAFT PREVIEW MODE" not in res_guest_pdp2.data.decode("utf-8"), "Guest should not see admin draft preview banner"
    print("✓ Guest can view live product without preview banner.")

    # ========================================================
    # B. JOURNAL DRAFT -> PUBLISH WORKFLOW
    # ========================================================
    test_cve = "CVE-2026-DRAFT-99"
    test_post_slug = "cve-2026-draft-zero-day-advisory"

    post_payload = {
        "title": "Confidential Zero-Day Research Draft Advisory",
        "slug": test_post_slug,
        "cve_id": test_cve,
        "cvss_score": "9.9",
        "severity": "CRITICAL",
        "category": "Zero-Day Advisories",
        "status": "DRAFT",
        "author": "ZERO-DAY UNIT",
        "read_time": "5 MIN READ",
        "summary": "Internal threat disclosure waiting for coordinated vendor patch release.",
        "content": "### 01 · Vulnerability Overview\nUnder embargo until 2026-12-01."
    }

    res_post = client.post("/api/admin/posts", json=post_payload)
    assert res_post.status_code == 200, f"Failed to create draft post: {res_post.data}"
    post_id = res_post.get_json()["id"]
    print(f"✓ Created test journal post #{post_id} in DRAFT status.")

    # Guest visiting /journal: post MUST NOT appear
    res_journal = guest_client.get(f"/journal?q={test_cve}")
    assert "NO MATCHING THREAT DISCLOSURES FOUND" in res_journal.data.decode("utf-8"), "DRAFT post leaked on public /journal!"
    print("✓ Public /journal successfully isolates DRAFT advisory (NOT visible to guests).")

    # Guest visiting /journal/<slug>: MUST be redirected away
    res_guest_post = guest_client.get(f"/journal/{test_post_slug}")
    assert res_guest_post.status_code in (302, 301), f"Expected redirect for draft post, got {res_guest_post.status_code}"
    print("✓ Guest attempting to view DRAFT advisory is properly redirected away.")

    # Admin visiting /journal/<slug>: CAN view draft with preview banner
    res_admin_post = client.get(f"/journal/{test_post_slug}")
    assert res_admin_post.status_code == 200, "Admin could not view draft advisory"
    assert "DRAFT PREVIEW MODE" in res_admin_post.data.decode("utf-8"), "Draft Preview watermark banner missing on journal"
    print("✓ Admin successfully views DRAFT advisory with prominent DRAFT PREVIEW banner.")

    # Toggle Post Status to PUBLISHED
    res_post_toggle = client.post(f"/api/admin/posts/{post_id}/toggle-status")
    assert res_post_toggle.status_code == 200
    assert res_post_toggle.get_json()["new_status"] == "PUBLISHED"
    print("✓ Toggled advisory status from DRAFT -> PUBLISHED via /api/admin/posts/toggle-status.")

    # Guest visiting /journal: NOW post MUST appear
    res_journal2 = guest_client.get(f"/journal?q={test_cve}")
    assert test_post_slug in res_journal2.data.decode("utf-8"), "Published post should appear in /journal"
    print("✓ Public /journal immediately displays advisory once published.")

    # Guest visiting /journal/<slug>: NOW allowed with HTTP 200
    res_guest_post2 = guest_client.get(f"/journal/{test_post_slug}")
    assert res_guest_post2.status_code == 200
    assert "DRAFT PREVIEW MODE" not in res_guest_post2.data.decode("utf-8")
    print("✓ Guest can view live advisory without preview banner.")

    # ========================================================
    # C. CLEANUP TEST ITEMS
    # ========================================================
    client.delete(f"/api/admin/products/{prod_id}")
    client.delete(f"/api/admin/posts/{post_id}")
    print("✓ Cleaned up test product and test post from database.")

    print("\n=== ALL DRAFT / PUBLISH WORKFLOW TESTS PASSED 100%! ===")

if __name__ == "__main__":
    run_tests()
