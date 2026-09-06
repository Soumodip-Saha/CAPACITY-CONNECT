import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db

def run_tests():
    print("=== STARTING COURSE & SYLLABUS EDITING TESTS ===")
    client = TestClient(app)

    # 1. Login as Trainer
    resp_trn = client.get("/auth/demo-login/trainer", follow_redirects=False)
    client.cookies.set("capacity_connect_session", resp_trn.cookies.get("capacity_connect_session"))

    # 2. Access "Edit Syllabus & Materials" page for Course 1
    manage_page = client.get("/trainer/courses/1/manage")
    assert manage_page.status_code == 200
    assert "Course Modules & Interactive Lessons" in manage_page.text
    assert "Edit Course Info" in manage_page.text
    assert "Add New Module" in manage_page.text
    print(" [PASS] 1. Manage / Edit Course page loads without Jinja2 template errors")

    # 3. Test Editing Course Metadata
    edit_resp = client.post("/trainer/courses/1/edit", data={
        "title": "Advanced Numerical Weather Prediction (NWP) & High-Resolution Modeling (Updated)",
        "domain": "Numerical Weather Prediction",
        "level": "Advanced",
        "duration_hours": "30",
        "description": "Updated syllabus with operational ensemble data assimilation."
    }, follow_redirects=True)
    assert edit_resp.status_code == 200
    assert "Course details updated successfully" in edit_resp.text
    assert "(Updated)" in edit_resp.text
    print(" [PASS] 2. Course details (title, domain, duration, description) edited successfully")

    # 4. Test Adding a Module
    add_mod_resp = client.post("/trainer/courses/1/modules/add", data={
        "title": "Module 99: Test Verification Module",
        "summary": "Testing module creation."
    }, follow_redirects=True)
    assert add_mod_resp.status_code == 200
    assert "Module 99: Test Verification Module" in add_mod_resp.text

    # Get newly created module ID
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM course_modules WHERE title = 'Module 99: Test Verification Module' AND course_id = 1")
        mod_id = cursor.fetchone()[0]
    print(f" [PASS] 3. Module added successfully (ID: {mod_id})")

    # 5. Test Editing Module
    edit_mod_resp = client.post(f"/trainer/courses/1/modules/{mod_id}/edit", data={
        "title": "Module 99: Renamed Verification Module",
        "summary": "Updated summary for testing."
    }, follow_redirects=True)
    assert edit_mod_resp.status_code == 200
    assert "Module 99: Renamed Verification Module" in edit_mod_resp.text
    print(" [PASS] 4. Module edited and renamed successfully")

    # 6. Test Adding a Lesson to Module
    add_les_resp = client.post("/trainer/courses/1/lessons/add", data={
        "module_id": str(mod_id),
        "title": "Lesson 99.1: Test Lecture",
        "lesson_type": "video",
        "duration_mins": "25",
        "content_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "notes": "Testing lesson notes."
    }, follow_redirects=True)
    assert add_les_resp.status_code == 200
    assert "Lesson 99.1: Test Lecture" in add_les_resp.text

    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM course_lessons WHERE title = 'Lesson 99.1: Test Lecture' AND module_id = ?", (mod_id,))
        lesson_id = cursor.fetchone()[0]
    print(f" [PASS] 5. Lesson added to module successfully (ID: {lesson_id})")

    # 7. Test Editing Lesson
    edit_les_resp = client.post(f"/trainer/courses/1/lessons/{lesson_id}/edit", data={
        "title": "Lesson 99.1: Renamed Lecture",
        "lesson_type": "document",
        "duration_mins": "35",
        "content_url": "/static/docs/sample.pdf",
        "notes": "Updated lesson notes."
    }, follow_redirects=True)
    assert edit_les_resp.status_code == 200
    assert "Lesson 99.1: Renamed Lecture" in edit_les_resp.text
    print(" [PASS] 6. Lesson edited and updated successfully")

    # 8. Test Deleting Lesson
    del_les_resp = client.post(f"/trainer/courses/1/lessons/{lesson_id}/delete", follow_redirects=True)
    assert del_les_resp.status_code == 200
    assert "Lesson 99.1: Renamed Lecture" not in del_les_resp.text
    print(" [PASS] 7. Lesson deleted successfully")

    # 9. Test Deleting Module
    del_mod_resp = client.post(f"/trainer/courses/1/modules/{mod_id}/delete", follow_redirects=True)
    assert del_mod_resp.status_code == 200
    assert "Module 99: Renamed Verification Module" not in del_mod_resp.text
    print(" [PASS] 8. Module and associated content deleted successfully")

    # 10. Test Uploading Course Study Material
    upload_mat_resp = client.post("/trainer/courses/1/materials/upload", data={
        "title": "NWP Operational Forecast Handbook 2026",
        "resource_type": "Technical Document",
        "file_size": "4.2 MB",
        "file_url": "/static/docs/NWP_Guide.pdf",
        "description": "Comprehensive reference handbook for numerical weather prediction."
    }, follow_redirects=True)
    assert upload_mat_resp.status_code == 200
    assert "Study material uploaded successfully" in upload_mat_resp.text
    assert "NWP Operational Forecast Handbook 2026" in upload_mat_resp.text
    print(" [PASS] 9. Course Study Material uploaded and rendered in syllabus view successfully")

    # Get material ID
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM trainer_library WHERE title = 'NWP Operational Forecast Handbook 2026'")
        mat_id = cursor.fetchone()[0]

    # 11. Test Deleting Course Study Material
    del_mat_resp = client.post(f"/trainer/courses/1/materials/{mat_id}/delete", follow_redirects=True)
    assert del_mat_resp.status_code == 200
    assert "Material deleted successfully" in del_mat_resp.text
    print(" [PASS] 10. Course Study Material removed cleanly")

    print("\n=== ALL COURSE & SYLLABUS EDITING TESTS PASSED 100%! ===")

if __name__ == "__main__":
    run_tests()

