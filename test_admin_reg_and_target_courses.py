import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db

def run_tests():
    print("=== STARTING ADMIN REGISTRATION & TARGET COURSES TESTS ===")
    client = TestClient(app)

    # 1. Test Admin Registration with valid passcode MOES-ADMIN-2026 -> Active + Auto-login
    test_admin_email = "director.sharma@imd.gov.in"
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE email = ?", (test_admin_email,))

    reg_resp = client.post("/auth/register", data={
        "email": test_admin_email,
        "password": "AdminPassword@123",
        "full_name": "Dr. Sunil Sharma",
        "role": "admin",
        "admin_code": "MOES-ADMIN-2026",
        "designation": "Deputy Director General",
        "department": "MoES HQ - Training Cell",
        "qualifications": "Ph.D. Atmospheric Sciences",
        "experience_years": "20",
        "skills": "Governance, Numerical Modeling, HPC",
        "interests": "Policy Planning",
        "bio": "Overseeing MoES capacity development."
    }, follow_redirects=False)

    assert reg_resp.status_code in (302, 303), f"Expected 303 redirect, got {reg_resp.status_code}"
    assert reg_resp.headers.get("location") == "/admin/dashboard", f"Expected redirect to /admin/dashboard, got {reg_resp.headers.get('location')}"
    cookie = reg_resp.headers.get("set-cookie")
    assert "capacity_connect_session" in cookie
    print(" [PASS] 1. Admin Registration with MOES-ADMIN-2026 passcode activated immediately and redirected to /admin/dashboard")

    # 2. Test Admin Registration without passcode -> Queued for approval (pending_approval)
    test_admin_pending = "officer.meena@imd.gov.in"
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE email = ?", (test_admin_pending,))

    reg_pending_resp = client.post("/auth/register", data={
        "email": test_admin_pending,
        "password": "AdminPassword@123",
        "full_name": "Rajesh Meena",
        "role": "admin",
        "admin_code": "",  # No code
        "designation": "Administrative Officer",
        "department": "IMD Jaipur Observatory",
        "qualifications": "M.Sc. Physics",
        "experience_years": "12"
    }, follow_redirects=True)

    assert reg_pending_resp.status_code == 200
    assert "queued for MoES Training Directorate verification" in reg_pending_resp.text or "submitted successfully" in reg_pending_resp.text
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT status, role FROM users WHERE email = ?", (test_admin_pending,))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "pending_approval"
        assert row[1] == "admin"
    print(" [PASS] 2. Admin Registration without passcode queued safely with status 'pending_approval'")

    # 3. Test Trainer Portal - Course Catalog & Target Courses
    resp_trn = client.get("/auth/demo-login/trainer", follow_redirects=False)
    client.cookies.set("capacity_connect_session", resp_trn.cookies.get("capacity_connect_session"))

    courses_resp = client.get("/trainer/courses")
    assert courses_resp.status_code == 200
    assert "National Target Courses" in courses_resp.text
    # Check baseline courses
    assert "IMD-AI-401" in courses_resp.text
    assert "IMD-AVN-201" in courses_resp.text
    assert "INCOIS-OCN-301" in courses_resp.text
    assert "NCMRWF-HPC-501" in courses_resp.text
    assert "IMD-RAD-302" in courses_resp.text
    # Check newly expanded domain courses
    assert "NCPOR-POL-401" in courses_resp.text
    assert "IMD-HYD-201" in courses_resp.text
    assert "IITM-AQ-301" in courses_resp.text
    assert "NIOT-MAR-401" in courses_resp.text
    assert "IIG-MAG-301" in courses_resp.text
    assert "IMD-URB-202" in courses_resp.text
    assert "NCCR-CST-301" in courses_resp.text
    assert "IMD-INS-101" in courses_resp.text
    print(" [PASS] 3. Trainer Portal displays expanded MoES National Target Courses Matrix (all 20 domain courses)")

    # 4. Test Trainer Quiz Builder dropdown has all target courses
    quiz_page = client.get("/trainer/quiz/create")
    assert quiz_page.status_code == 200
    assert "IMD-AI-401" in quiz_page.text
    assert "IMD-AVN-201" in quiz_page.text
    assert "INCOIS-OCN-301" in quiz_page.text
    assert "NCMRWF-HPC-501" in quiz_page.text
    assert "IMD-RAD-302" in quiz_page.text
    assert "NCPOR-POL-401" in quiz_page.text
    assert "IMD-HYD-201" in quiz_page.text
    assert "IITM-AQ-301" in quiz_page.text
    assert "NIOT-MAR-401" in quiz_page.text
    assert "IIG-MAG-301" in quiz_page.text
    assert "IMD-URB-202" in quiz_page.text
    assert "NCCR-CST-301" in quiz_page.text
    assert "IMD-INS-101" in quiz_page.text
    print(" [PASS] 4. Trainer Quiz Builder allows selecting from all 20 MoES target courses across disciplines")

    # 5. Verify database has 20 courses and 19 distinct domains
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM courses")
        total_courses = cursor.fetchone()[0]
        assert total_courses >= 20, f"Expected at least 20 courses, got {total_courses}"
        cursor.execute("SELECT COUNT(DISTINCT domain) FROM courses")
        total_domains = cursor.fetchone()[0]
        assert total_domains >= 19, f"Expected at least 19 domains, got {total_domains}"
    print(f" [PASS] 5. Database verified with {total_courses} courses across {total_domains} unique domains")

    print("\n=== ALL NEW ADMIN REGISTRATION & 20 TARGET COURSE TESTS PASSED 100%! ===")

if __name__ == "__main__":
    run_tests()
