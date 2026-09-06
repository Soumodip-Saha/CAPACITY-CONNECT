import os
import sys
sys.path.insert(0, os.path.abspath("."))
from datetime import datetime, date

from app.database import get_db, UniversalRow
from app.services.certificate_service import enrich_certificate_timestamps, verify_certificate_by_id
from fastapi.testclient import TestClient
from app.main import app

def test_universal_row():
    print("Testing UniversalRow date vs datetime...")
    test_date = date(2026, 8, 24)
    test_datetime = datetime(2026, 8, 24, 15, 30, 45)
    
    row_date = UniversalRow([test_date], ["d"])
    row_datetime = UniversalRow([test_datetime], ["dt"])
    
    assert row_date["d"] == "2026-08-24", f"Expected 2026-08-24, got {row_date['d']}"
    assert row_datetime["dt"] == "2026-08-24 15:30:45", f"Expected 2026-08-24 15:30:45, got {row_datetime['dt']}"
    print("PASS: UniversalRow formats date and datetime correctly without 00:00:00 bleed.")

def test_enrichment():
    print("Testing enrich_certificate_timestamps...")
    cert_data = {
        "certificate_id": "TEST-CERT-01",
        "issue_date": "2026-08-24",
        "created_at": "2026-08-24 14:35:22"
    }
    enriched = enrich_certificate_timestamps(cert_data)
    print("Enriched result:", enriched)
    assert enriched["formatted_date"] == "24 August 2026"
    assert enriched["formatted_time"] == "02:35 PM IST"
    assert enriched["formatted_time_24h"] == "14:35:22 IST"
    assert "24 August 2026" in enriched["formatted_datetime"]
    assert "02:35 PM IST" in enriched["formatted_datetime"]
    assert enriched["formatted_timestamp"] == "24-Aug-2026 14:35:22 IST"
    print("PASS: enrich_certificate_timestamps test passed.")

def test_verify_endpoint():
    print("Testing /verify/certificate/{cert_id} endpoint...")
    client = TestClient(app)
    
    with get_db() as db:
        cur = db.cursor()
        cur.execute("SELECT certificate_id FROM certificates LIMIT 1")
        row = cur.fetchone()
        if not row:
            print("No certificates found in DB to test.")
            return
        cert_id = row["certificate_id"]
    
    response = client.get(f"/verify/certificate/{cert_id}")
    assert response.status_code == 200
    html = response.text
    print(f"Checking HTML for {cert_id}...")
    assert "Issue Date &amp; Time" in html or "Issue Date & Time" in html
    assert "00:00:00" not in html, "00:00:00 should not appear in HTML!"
    assert "Timestamped on Government Record" in html
    assert "IST" in html
    print("PASS: /verify/certificate endpoint displays valid date and time in IST!")

def test_trainee_certificate_view():
    print("Testing /trainee/certificate/{cert_id} endpoint with trainee auth...")
    client = TestClient(app)
    
    with get_db() as db:
        cur = db.cursor()
        cur.execute("SELECT u.id, u.email, u.role, cert.certificate_id FROM certificates cert JOIN users u ON u.id = cert.user_id WHERE u.role = 'trainee' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("SELECT u.id, u.email, u.role, cert.certificate_id FROM certificates cert JOIN users u ON u.id = cert.user_id LIMIT 1")
            row = cur.fetchone()
        user_id = row["id"]
        email = row["email"]
        role = row["role"]
        cert_id = row["certificate_id"]

    from app.auth import create_session_token
    from app.config import SESSION_COOKIE_NAME
    token = create_session_token(user_id, email, role)
    client.cookies.set(SESSION_COOKIE_NAME, token)
        
    res = client.get(f"/trainee/certificate/{cert_id}")
    print("Cert page status:", res.status_code)
    assert res.status_code == 200
    html = res.text
    assert "Date of Issue" in html
    assert "Time of Issuance" in html
    assert "00:00:00" not in html
    assert "IST" in html
    print(f"PASS: /trainee/certificate/{cert_id} rendered cleanly with Time of Issuance!")

def test_dashboard_view():
    print("Testing /trainee/dashboard view...")
    client = TestClient(app)
    with get_db() as db:
        cur = db.cursor()
        cur.execute("SELECT id, email, role FROM users WHERE role = 'trainee' LIMIT 1")
        row = cur.fetchone()
        user_id = row["id"]
        email = row["email"]
        role = row["role"]

    from app.auth import create_session_token
    from app.config import SESSION_COOKIE_NAME
    token = create_session_token(user_id, email, role)
    client.cookies.set(SESSION_COOKIE_NAME, token)

    res = client.get("/trainee/dashboard")
    assert res.status_code == 200
    html = res.text
    assert "00:00:00" not in html
    print("PASS: /trainee/dashboard rendered cleanly without 00:00:00!")

if __name__ == "__main__":
    test_universal_row()
    test_enrichment()
    test_verify_endpoint()
    test_trainee_certificate_view()
    test_dashboard_view()
    print("\nALL CERTIFICATE TIME TESTS PASSED SUCCESSFULLY!")
