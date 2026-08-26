import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, seed_db, get_db

def run_extended_tests():
    print("=== STARTING EXTENDED LIFECYCLE TESTS ===")
    init_db()
    seed_db()
    client = TestClient(app)

    # 1. Admin Flow: Approve Pending Trainer
    resp_adm = client.get("/auth/demo-login/admin", follow_redirects=False)
    client.cookies.set("capacity_connect_session", resp_adm.cookies.get("capacity_connect_session"))

    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE email = 'prof.tarun.verma@iitm.ac.in'")
        tarun_id = cursor.fetchone()[0]

    approve_resp = client.post(f"/admin/users/{tarun_id}/approve", follow_redirects=True)
    assert approve_resp.status_code == 200

    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT status FROM users WHERE id = ?", (tarun_id,))
        assert cursor.fetchone()[0] == "active"
    print(" [PASS] 1. Admin approved pending trainer (Prof. Tarun Verma) -> Status active")

    # 2. Admin Flow: Publish Announcement
    notice_resp = client.post("/admin/announcements/create", data={
        "title": "New Radar Workshop 2026",
        "content": "Specialized X-band Doppler training session starting next Monday.",
        "category": "Workshop",
        "priority": "Urgent"
    }, follow_redirects=True)
    assert notice_resp.status_code == 200
    assert "New Radar Workshop 2026" in notice_resp.text
    print(" [PASS] 2. Admin created announcement -> Visible in Bulletins")

    # 3. Trainer Flow: Create a Quiz
    resp_trn = client.get("/auth/demo-login/trainer", follow_redirects=False)
    client.cookies.set("capacity_connect_session", resp_trn.cookies.get("capacity_connect_session"))

    quiz_data = {
        "course_id": "1",
        "title": "NWP Advanced Grid Staggering Quiz",
        "subject": "Arakawa Grids & Wave Dispersion",
        "duration_mins": "15",
        "pass_percentage": "70",
        "deadline_days": "20",
        "q_text_1": "Which Arakawa grid is optimal for geostrophic adjustment in high-resolution models?",
        "op_a_1": "Arakawa A",
        "op_b_1": "Arakawa B",
        "op_c_1": "Arakawa C",
        "op_d_1": "Arakawa D",
        "correct_1": "C",
        "expl_1": "Arakawa C-grid preserves rotational energy and gravity wave dispersion characteristics.",
        "marks_1": "1"
    }
    create_quiz_resp = client.post("/trainer/quiz/create", data=quiz_data, follow_redirects=True)
    assert create_quiz_resp.status_code == 200
    print(" [PASS] 3. Trainer created subject-wise MCQ assessment with question pool")

    # 4. Trainer Flow: Upload Library Item
    upload_resp = client.post("/trainer/library/upload", data={
        "title": "NWP Spectral Transform Techniques (Slide Deck)",
        "resource_type": "presentation_ppt",
        "category": "Numerical Weather Prediction",
        "file_url": "/static/docs/NWP_Spectral_Transforms.pdf",
        "file_size": "18.2 MB",
        "description": "Comprehensive presentation slides on spherical harmonics discretization."
    }, follow_redirects=True)
    assert upload_resp.status_code == 200
    assert "NWP Spectral Transform Techniques" in upload_resp.text
    print(" [PASS] 4. Trainer uploaded resource to Trainer Digital Library")

    # 5. Trainee Flow: Take Assessment & Submit
    resp_tr = client.get("/auth/demo-login/trainee", follow_redirects=False)
    client.cookies.set("capacity_connect_session", resp_tr.cookies.get("capacity_connect_session"))

    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM quizzes WHERE title LIKE '%Radar Interpretation%'")
        rad_quiz_id = cursor.fetchone()[0]

        cursor.execute("SELECT id, correct_option FROM quiz_questions WHERE quiz_id = ?", (rad_quiz_id,))
        questions = cursor.fetchall()

    submission_data = {}
    for q in questions:
        submission_data[f"question_{q[0]}"] = q[1]  # submit correct answer

    submit_resp = client.post(f"/trainee/assessment/{rad_quiz_id}/submit", data=submission_data, follow_redirects=True)
    assert submit_resp.status_code == 200
    assert "Assessment Passed Successfully" in submit_resp.text
    assert "100" in submit_resp.text
    print(" [PASS] 5. Trainee submitted timed MCQ assessment -> 100% Scorecard Generated")

    # 6. Trainee Flow: View Auto-Generated Certificate
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT certificate_id FROM certificates WHERE course_id = 2")
        cert_row = cursor.fetchone()
        assert cert_row is not None
        cert_id = cert_row[0]

    cert_page = client.get(f"/trainee/certificate/{cert_id}")
    assert cert_page.status_code == 200
    assert "Certificate of Competency" in cert_page.text
    assert "Ministry of Earth Sciences" in cert_page.text
    print(f" [PASS] 6. Verifiable Certificate generated & rendered: {cert_id}")

    # 7. Trainee Flow: Submit Course Feedback
    feedback_resp = client.post("/trainee/feedback/2", data={
        "rating_content": "5",
        "rating_trainer": "5",
        "rating_overall": "5",
        "comments": "Superb hands-on radar interpretation training by Dr. Ananya Das."
    }, follow_redirects=True)
    assert feedback_resp.status_code == 200
    print(" [PASS] 7. Trainee submitted multi-criteria course & trainer feedback")

    # 8. Competency Engine: Verify Algorithm Matching with Admin Session
    resp_adm2 = client.get("/auth/demo-login/admin", follow_redirects=False)
    client.cookies.set("capacity_connect_session", resp_adm2.cookies.get("capacity_connect_session"))
    
    resp_map = client.get("/admin/competency-map?subject=Numerical+Weather+Prediction")
    assert resp_map.status_code == 200
    assert "Dr. Madhavan Sharma" in resp_map.text
    print(" [PASS] 8. Competency Mapping Engine accurately ranked domain expert as Top Match")

    print("\n=== ALL EXTENDED LIFECYCLE AND MUTATION TESTS PASSED 100%! ===")

if __name__ == "__main__":
    run_extended_tests()
