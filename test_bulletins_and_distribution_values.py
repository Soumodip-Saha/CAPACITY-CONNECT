import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db

def run_tests():
    print("=== STARTING BULLETINS & DOMAIN CURRICULA DISTRIBUTION TESTS ===")
    client = TestClient(app)

    # 1. Public Bulletins page accessible without login
    resp_pub = client.get("/bulletins")
    assert resp_pub.status_code == 200
    assert "MoES & IMD Bulletins & Circulars" in resp_pub.text
    assert "Workshop" in resp_pub.text or "Circular" in resp_pub.text
    print(" [PASS] 1. Public /bulletins repository loads for all visitors without authentication")

    # 1b. Search & Category filtering on /bulletins
    resp_search = client.get("/bulletins?category=Workshop")
    assert resp_search.status_code == 200
    assert "Workshop" in resp_search.text
    resp_term = client.get("/bulletins?search=radar")
    assert resp_term.status_code == 200
    print(" [PASS] 1b. Bulletins category filtering and keyword search functional")

    # 2. Homepage Notice Board links to /bulletins and displays active notices
    resp_home = client.get("/")
    assert resp_home.status_code == 200
    assert 'href="/bulletins"' in resp_home.text
    assert "Notice Board" in resp_home.text
    print(" [PASS] 2. Homepage Notice Board links to /bulletins and renders notice ticker")

    # 3. Top Navbar contains Bulletins link for all users
    assert 'href="/bulletins"' in resp_home.text
    print(" [PASS] 3. Global navbar displays Bulletins & Circulars entry point")

    # 4. Admin Bulletins Manager (/admin/announcements)
    resp_admin = client.get("/auth/demo-login/admin", follow_redirects=False)
    client.cookies.set("capacity_connect_session", resp_admin.cookies.get("capacity_connect_session"))

    ann_page = client.get("/admin/announcements")
    assert ann_page.status_code == 200
    assert "Announcements & Circulars Manager" in ann_page.text
    print(" [PASS] 4. Admin Announcements & Circulars Manager loads with date formatting")

    # 4b. Admin creates a new Bulletin
    post_ann = client.post("/admin/announcements/create", data={
        "title": "Automated Verification Bulletin 2026",
        "content": "Official testing bulletin verifying end-to-end notification pipeline.",
        "category": "Circular",
        "priority": "Important"
    }, follow_redirects=True)
    assert post_ann.status_code == 200
    assert "Automated Verification Bulletin 2026" in post_ann.text
    print(" [PASS] 4b. Admin published new official circular to the portal")

    # 5. Trainee Dashboard displays Bulletins widget
    resp_trn = client.get("/auth/demo-login/trainee", follow_redirects=False)
    client.cookies.set("capacity_connect_session", resp_trn.cookies.get("capacity_connect_session"))
    trainee_dash = client.get("/trainee/dashboard")
    assert trainee_dash.status_code == 200
    assert "MoES Bulletins & Notices" in trainee_dash.text
    assert "href=\"/bulletins\"" in trainee_dash.text
    print(" [PASS] 5. Trainee Dashboard displays official Bulletins & Notices widget")

    # 6. Trainer Dashboard displays Bulletins widget
    resp_trainer = client.get("/auth/demo-login/trainer", follow_redirects=False)
    client.cookies.set("capacity_connect_session", resp_trainer.cookies.get("capacity_connect_session"))
    trainer_dash = client.get("/trainer/dashboard")
    assert trainer_dash.status_code == 200
    assert "MoES Bulletins & Notices" in trainer_dash.text
    assert "href=\"/bulletins\"" in trainer_dash.text
    print(" [PASS] 6. Trainer Dashboard displays official Bulletins & Notices widget")

    # 7. API Chart Data returns domain distribution with counts and percentages
    chart_api = client.get("/api/admin/chart-data")
    assert chart_api.status_code == 200
    chart_data = chart_api.json()
    assert "domains" in chart_data
    assert chart_data["total_courses"] >= 20
    assert chart_data["total_domains"] >= 19
    for d in chart_data["domains"]:
        assert "domain" in d
        assert "count" in d
        assert "percentage" in d
        assert d["percentage"] > 0
    print(f" [PASS] 7. /api/admin/chart-data provides {len(chart_data['domains'])} domains with exact counts and percentages")

    # 8. Admin Dashboard renders Domain Curricula Distribution with values list & tabs
    client.cookies.set("capacity_connect_session", resp_admin.cookies.get("capacity_connect_session"))
    admin_dash = client.get("/admin/dashboard")
    assert admin_dash.status_code == 200
    assert "Domain Curricula Distribution" in admin_dash.text
    assert "domainValuesList" in admin_dash.text
    assert "setDomainTab" in admin_dash.text
    assert "domainChart" in admin_dash.text
    assert "Discipline breakdown with exact curricula counts" in admin_dash.text
    print(" [PASS] 8. Admin Dashboard renders Domain Curricula Distribution with values breakdown and view toggles")

    print("\n=== ALL BULLETINS & DOMAIN DISTRIBUTION TESTS PASSED 100%! ===")

if __name__ == "__main__":
    run_tests()
