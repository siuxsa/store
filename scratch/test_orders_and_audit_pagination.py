import json
from app import app
from bs4 import BeautifulSoup

def test_pages():
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["admin_logged_in"] = True
            sess["admin_id"] = 1
            sess["admin_username"] = "admin"
            sess["admin_role"] = "ADMIN"
        
        res = c.get("/admin")
        assert res.status_code == 200
        soup = BeautifulSoup(res.data.decode("utf-8"), "html.parser")

        # 1. Orders
        orders_table = soup.find("table", id="orders-table")
        assert orders_table is not None, "orders-table not found"
        orders_search = soup.find("input", id="orders-search-input")
        assert orders_search is not None, "orders-search-input not found"
        orders_bar = soup.find("div", id="orders-pagination-bar")
        assert orders_bar is not None, "orders-pagination-bar not found"
        assert orders_bar.find("button", id="btn-orders-prev") is not None
        assert orders_bar.find("button", id="btn-orders-next") is not None
        assert orders_bar.find("strong", id="orders-page-range") is not None
        assert orders_bar.find("strong", id="orders-total-count") is not None
        assert orders_bar.find("span", id="orders-current-page") is not None
        assert orders_bar.find("span", id="orders-total-pages") is not None

        # 2. Audit Logs
        audit_table = soup.find("table", id="audit-table")
        assert audit_table is not None, "audit-table not found"
        audit_search = soup.find("input", id="audit-search-input")
        assert audit_search is not None, "audit-search-input not found"
        audit_bar = soup.find("div", id="audit-pagination-bar")
        assert audit_bar is not None, "audit-pagination-bar not found"
        assert audit_bar.find("button", id="btn-audit-prev") is not None
        assert audit_bar.find("button", id="btn-audit-next") is not None
        assert audit_bar.find("strong", id="audit-page-range") is not None
        assert audit_bar.find("strong", id="audit-total-count") is not None
        assert audit_bar.find("span", id="audit-current-page") is not None
        assert audit_bar.find("span", id="audit-total-pages") is not None

        print("Test passed: Orders and Audit modules have complete pagination and search UI elements!")

if __name__ == "__main__":
    test_pages()
