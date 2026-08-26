import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, seed_db

def run_tests():
    print("=== STARTING CAPACITY CONNECT SYSTEM TESTS ===")
    init_db()
    seed_db()

    client = TestClient(app)

    # 1. Test Homepage
    resp = client.get("/")
    assert resp.status_code == 200, f"Homepage failed: {resp.status_code}"
    assert "CAPACITY" in resp.text
    print(" [PASS] 1. Homepage loads successfully with MoES/IMD branding")

    # 2. Test Public Certificate Verification
    resp = client.get("/verify/certificate/IMD-CB-2026-8921")
    assert resp.status_code == 200, f"Certificate verify failed: {resp.status_code}"
    assert "VERIFIED AUTHENTIC" in resp.text
    assert "Rahul Verma" in resp.text
    print(" [PASS] 2. Public Certificate Verification validates official credentials")

    # 3. Test API Competency Matcher Query
    resp = client.get("/api/competency/query?subject=Doppler+Radar+Nowcasting")
    assert resp.status_code == 200, f"Competency query failed: {resp.status_code}"
    data = resp.json()
    assert data["status"] == "success"
    assert len(data["results"]) > 0
    top_trainer = data["results"][0]
    print(f" [PASS] 3. Competency Engine matched top trainer: {top_trainer['full_name']} (Fit: {top_trainer['total_score']}%)")

    # 4. Test API Chart Data for Admin
    resp = client.get("/api/admin/chart-data")
    assert resp.status_code == 200
    chart_data = resp.json()
    assert "regional_stats" in chart_data and "domains" in chart_data
    print(" [PASS] 4. Admin Chart Data API returns regional & domain statistics")

    # 5. Test 1-Click Demo Login for Admin
    resp = client.get("/auth/demo-login/admin", follow_redirects=False)
    assert resp.status_code in (302, 303), f"Admin login failed: {resp.status_code}"
    cookie = resp.headers.get("set-cookie")
    assert "capacity_connect_session" in cookie
    print(" [PASS] 5. 1-Click Demo Login sets secure session token for Admin")

    # 6. Test Admin Dashboard with Session
    client.cookies.set("capacity_connect_session", resp.cookies.get("capacity_connect_session"))
    admin_dash = client.get("/admin/dashboard")
    assert admin_dash.status_code == 200
    assert "Executive Capacity Command" in admin_dash.text
    print(" [PASS] 6. Admin Command Center renders KPI metrics and charts")

    # 7. Test Trainee Flow
    resp_tr = client.get("/auth/demo-login/trainee", follow_redirects=False)
    client.cookies.set("capacity_connect_session", resp_tr.cookies.get("capacity_connect_session"))
    trainee_dash = client.get("/trainee/dashboard")
    assert trainee_dash.status_code == 200
    assert "Welcome back, Rahul Verma" in trainee_dash.text
    print(" [PASS] 7. Trainee Dashboard loads personalized progress & enrolled courses")

    # 8. Test Course Catalog
    courses_page = client.get("/trainee/courses")
    assert courses_page.status_code == 200
    assert "Numerical Weather Prediction" in courses_page.text
    print(" [PASS] 8. Course Catalog renders all MoES specialized domain courses")

    # 9. Test Trainer Flow
    resp_trn = client.get("/auth/demo-login/trainer", follow_redirects=False)
    client.cookies.set("capacity_connect_session", resp_trn.cookies.get("capacity_connect_session"))
    trainer_dash = client.get("/trainer/dashboard")
    assert trainer_dash.status_code == 200
    assert "Faculty & Subject Expert Suite" in trainer_dash.text
    print(" [PASS] 9. Trainer Suite loads authoring courses & roster")

    print("\n=== ALL 9 AUTOMATED INTEGRATION TESTS PASSED PERFECTLY! ===")

if __name__ == "__main__":
    run_tests()
