import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "http://127.0.0.1:5000"

def test_reviews_curation():
    print("=== TESTING HOMEPAGE REVIEWS SHOWCASE CURATION (4 TO 6+ REVIEWS) ===")
    session = requests.Session()

    # 1. Block unauthenticated curation
    res_unauth = requests.post(f"{BASE_URL}/api/admin/reviews/curation", json={"reviews": [1, 2, 3, 4]})
    assert res_unauth.status_code in [302, 401, 403], f"Expected auth block, got {res_unauth.status_code}"
    print("✓ Unauthenticated access to /api/admin/reviews/curation properly blocked.")

    # 2. Authenticate as Master Admin
    res_login = session.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"})
    assert res_login.status_code == 200 or res_login.history, "Failed to login as admin"
    print("✓ Master Admin authenticated successfully.")

    # 3. Check admin page has curator container and buttons
    res_admin = session.get(f"{BASE_URL}/admin")
    assert res_admin.status_code == 200
    soup_admin = BeautifulSoup(res_admin.text, "html.parser")
    curator_box = soup_admin.find(id="curate-reviews-slots-grid")
    assert curator_box is not None, "Failed to find #curate-reviews-slots-grid in admin panel"
    print("✓ Found #curate-reviews-slots-grid in admin panel.")

    # 4. Save a custom 4-review showcase: [3, 1, 4, 2]
    custom_4 = [3, 1, 4, 2]
    res_save4 = session.post(f"{BASE_URL}/api/admin/reviews/curation", json={"reviews": custom_4})
    assert res_save4.status_code == 200, f"Save 4 reviews failed: {res_save4.text}"
    data4 = res_save4.json()
    assert data4.get("ok") is True
    print("✓ Saved custom 4-review showcase [3, 1, 4, 2] via API.")

    # 5. Verify public homepage has exactly these 4 reviews in that order
    res_home4 = requests.get(f"{BASE_URL}/")
    assert res_home4.status_code == 200
    soup_home4 = BeautifulSoup(res_home4.text, "html.parser")
    cards4 = soup_home4.find_all("a", class_="manifesto-stream-card")
    # There are 2 sets for infinite loop (set 1 + duplicate set 2)
    assert len(cards4) == 8, f"Expected 8 cards (4 x 2 loop), got {len(cards4)}"
    first_4_authors = [c.find("div", class_="stream-author-name").get_text(strip=True) for c in cards4[:4]]
    print("✓ Public homepage renders 4 reviews in exact sequence:", first_4_authors)
    # Check that author from review #3 (Henrik Lindqvist) is first
    assert "Henrik" in first_4_authors[0], f"Expected Henrik first, got {first_4_authors[0]}"
    assert "Marcus" in first_4_authors[1], f"Expected Marcus second, got {first_4_authors[1]}"

    # 6. Save a custom 6-review showcase: [6, 5, 4, 3, 2, 1]
    custom_6 = [6, 5, 4, 3, 2, 1]
    res_save6 = session.post(f"{BASE_URL}/api/admin/reviews/curation", json={"reviews": custom_6})
    assert res_save6.status_code == 200, f"Save 6 reviews failed: {res_save6.text}"
    data6 = res_save6.json()
    assert data6.get("ok") is True
    print("✓ Saved custom 6-review showcase [6, 5, 4, 3, 2, 1] via API.")

    # 7. Verify public homepage has exactly 6 reviews (12 with infinite loop duplicate)
    res_home6 = requests.get(f"{BASE_URL}/")
    assert res_home6.status_code == 200
    soup_home6 = BeautifulSoup(res_home6.text, "html.parser")
    cards6 = soup_home6.find_all("a", class_="manifesto-stream-card")
    assert len(cards6) == 12, f"Expected 12 cards (6 x 2 loop), got {len(cards6)}"
    first_6_authors = [c.find("div", class_="stream-author-name").get_text(strip=True) for c in cards6[:6]]
    print("✓ Public homepage dynamically streams 6 reviews in exact sequence:", first_6_authors)
    # Check that review #6 (Dr. Aris Thorne) is first
    assert "Aris" in first_6_authors[0], f"Expected Dr. Aris first, got {first_6_authors[0]}"
    assert "Siddharth" in first_6_authors[1], f"Expected Siddharth second, got {first_6_authors[1]}"

    print("\n=== ALL HOMEPAGE REVIEWS SHOWCASE CURATION TESTS PASSED 100%! ===")

if __name__ == "__main__":
    test_reviews_curation()
