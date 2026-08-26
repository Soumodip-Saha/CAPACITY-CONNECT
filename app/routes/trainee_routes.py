import json
from datetime import datetime, date
from typing import Optional
from fastapi import APIRouter, Request, Form, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.auth import require_auth, get_current_user_from_request
from app.database import get_db
from app.services.certificate_service import generate_certificate_id, calculate_grade

router = APIRouter(prefix="/trainee", tags=["trainee"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
def trainee_dashboard(request: Request):
    user = require_auth(request, allowed_roles=["trainee", "admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        
        # Enrolled courses
        cursor.execute("""
            SELECT e.id as enrollment_id, e.progress_percent, e.status as enrollment_status, e.enrolled_at,
                   c.id as course_id, c.title, c.code, c.domain, c.level, c.duration_hours,
                   u.full_name as trainer_name,
                   (SELECT COUNT(*) FROM course_lessons WHERE course_id = c.id) as total_lessons,
                   (SELECT COUNT(*) FROM quizzes WHERE course_id = c.id AND is_active = 1) as quiz_count
            FROM enrollments e
            JOIN courses c ON c.id = e.course_id
            LEFT JOIN users u ON u.id = c.trainer_id
            WHERE e.user_id = ?
            ORDER BY e.enrolled_at DESC
        """, (user["id"],))
        enrollments = [dict(row) for row in cursor.fetchall()]

        # Recommended Courses (not enrolled yet)
        enrolled_ids = [e["course_id"] for e in enrollments]
        placeholders = ",".join("?" * len(enrolled_ids)) if enrolled_ids else "0"
        cursor.execute(f"""
            SELECT c.id, c.title, c.code, c.domain, c.level, c.duration_hours, c.description,
                   u.full_name as trainer_name
            FROM courses c
            LEFT JOIN users u ON u.id = c.trainer_id
            WHERE c.status = 'published' AND c.id NOT IN ({placeholders})
            LIMIT 4
        """, enrolled_ids if enrolled_ids else [])
        recommended = [dict(row) for row in cursor.fetchall()]

        # Certificates earned
        cursor.execute("""
            SELECT cert.id, cert.certificate_id, cert.issue_date, cert.grade, cert.score_percentage,
                   c.title as course_title, c.code as course_code
            FROM certificates cert
            JOIN courses c ON c.id = cert.course_id
            WHERE cert.user_id = ?
            ORDER BY cert.issue_date DESC
        """, (user["id"],))
        certificates = [dict(row) for row in cursor.fetchall()]

        # Available / Upcoming Quizzes
        cursor.execute("""
            SELECT q.id as quiz_id, q.title as quiz_title, q.duration_mins, q.pass_percentage, q.deadline,
                   c.title as course_title, c.id as course_id,
                   (SELECT COUNT(*) FROM quiz_questions WHERE quiz_id = q.id) as question_count,
                   (SELECT MAX(percentage) FROM quiz_attempts WHERE quiz_id = q.id AND user_id = ?) as best_score,
                   (SELECT MAX(is_passed) FROM quiz_attempts WHERE quiz_id = q.id AND user_id = ?) as has_passed
            FROM quizzes q
            JOIN courses c ON c.id = q.course_id
            JOIN enrollments e ON e.course_id = c.id
            WHERE e.user_id = ? AND q.is_active = 1
        """, (user["id"], user["id"], user["id"]))
        quizzes = [dict(row) for row in cursor.fetchall()]

        # Announcements
        cursor.execute("SELECT id, title, content, category, priority, created_at FROM announcements WHERE is_active = 1 ORDER BY created_at DESC LIMIT 3")
        announcements = [dict(row) for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="trainee/dashboard.html", context={
        "request": request,
        "user": user,
        "enrollments": enrollments,
        "recommended": recommended,
        "certificates": certificates,
        "quizzes": quizzes,
        "announcements": announcements
    })

@router.get("/profile", response_class=HTMLResponse)
def trainee_profile(request: Request):
    user = require_auth(request, allowed_roles=["trainee", "admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT cert.certificate_id, cert.issue_date, cert.grade, cert.score_percentage,
                   c.title as course_title, c.code as course_code
            FROM certificates cert
            JOIN courses c ON c.id = cert.course_id
            WHERE cert.user_id = ?
            ORDER BY cert.issue_date DESC
        """, (user["id"],))
        certificates = [dict(row) for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="trainee/profile.html", context={
        "request": request,
        "user": user,
        "certificates": certificates,
        "success": None,
        "error": None
    })

@router.post("/profile")
def update_trainee_profile(
    request: Request,
    full_name: str = Form(...),
    designation: str = Form(""),
    department: str = Form(""),
    qualifications: str = Form(""),
    experience_years: int = Form(0),
    skills: str = Form(""),
    interests: str = Form(""),
    bio: str = Form("")
):
    user = require_auth(request, allowed_roles=["trainee", "admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE users
            SET full_name = ?, designation = ?, department = ?, qualifications = ?,
                experience_years = ?, skills = ?, interests = ?, bio = ?
            WHERE id = ?
        """, (
            full_name.strip(), designation.strip(), department.strip(), qualifications.strip(),
            experience_years, skills.strip(), interests.strip(), bio.strip(), user["id"]
        ))
        
        # Refresh user object
        cursor.execute("SELECT * FROM users WHERE id = ?", (user["id"],))
        updated_user = dict(cursor.fetchone())

        cursor.execute("""
            SELECT cert.certificate_id, cert.issue_date, cert.grade, cert.score_percentage,
                   c.title as course_title, c.code as course_code
            FROM certificates cert
            JOIN courses c ON c.id = cert.course_id
            WHERE cert.user_id = ?
            ORDER BY cert.issue_date DESC
        """, (user["id"],))
        certificates = [dict(row) for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="trainee/profile.html", context={
        "request": request,
        "user": updated_user,
        "certificates": certificates,
        "success": "Your professional profile has been updated successfully!",
        "error": None
    })

@router.get("/courses", response_class=HTMLResponse)
def trainee_courses(request: Request, domain: str = "", search: str = "", level: str = ""):
    user = require_auth(request, allowed_roles=["trainee", "admin"])
    
    query = """
        SELECT c.id, c.title, c.code, c.domain, c.level, c.duration_hours, c.description,
               u.full_name as trainer_name, u.designation as trainer_designation,
               (SELECT COUNT(*) FROM enrollments WHERE course_id = c.id) as enrolled_count,
               (SELECT COUNT(*) FROM course_lessons WHERE course_id = c.id) as lessons_count,
               (SELECT e.id FROM enrollments e WHERE e.course_id = c.id AND e.user_id = ?) as user_enrollment_id,
               (SELECT e.progress_percent FROM enrollments e WHERE e.course_id = c.id AND e.user_id = ?) as user_progress
        FROM courses c
        LEFT JOIN users u ON u.id = c.trainer_id
        WHERE c.status = 'published'
    """
    params = [user["id"], user["id"]]

    if domain:
        query += " AND c.domain = ?"
        params.append(domain)
    if level:
        query += " AND c.level = ?"
        params.append(level)
    if search:
        query += " AND (c.title LIKE ? OR c.description LIKE ? OR c.code LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    query += " ORDER BY c.id ASC"

    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(query, params)
        courses = [dict(row) for row in cursor.fetchall()]

        # All distinct domains for filter pills
        cursor.execute("SELECT DISTINCT domain FROM courses WHERE status = 'published'")
        domains = [next(iter(row.values())) if isinstance(row, dict) else row[0] for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="trainee/courses.html", context={
        "request": request,
        "user": user,
        "courses": courses,
        "domains": domains,
        "selected_domain": domain,
        "selected_level": level,
        "search": search
    })

@router.post("/enroll/{course_id}")
def enroll_course(request: Request, course_id: int):
    user = require_auth(request, allowed_roles=["trainee", "admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM enrollments WHERE user_id = ? AND course_id = ?", (user["id"], course_id))
        existing = cursor.fetchone()
        if not existing:
            cursor.execute("""
                INSERT INTO enrollments (user_id, course_id, progress_percent, completed_lessons, status)
                VALUES (?, ?, 0, '[]', 'in_progress')
            """, (user["id"], course_id))

    return RedirectResponse(url=f"/trainee/courses/{course_id}", status_code=303)

@router.get("/courses/{course_id}", response_class=HTMLResponse)
def course_learning_portal(request: Request, course_id: int, active_lesson: Optional[int] = None):
    user = require_auth(request, allowed_roles=["trainee", "admin", "trainer"])
    
    with get_db() as db:
        cursor = db.cursor()
        
        # Course details
        cursor.execute("""
            SELECT c.*, u.full_name as trainer_name, u.designation as trainer_designation,
                   u.department as trainer_department, u.qualifications as trainer_qualifications,
                   u.bio as trainer_bio
            FROM courses c
            LEFT JOIN users u ON u.id = c.trainer_id
            WHERE c.id = ?
        """, (course_id,))
        course = cursor.fetchone()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        course = dict(course)

        # Check Enrollment
        cursor.execute("SELECT * FROM enrollments WHERE user_id = ? AND course_id = ?", (user["id"], course_id))
        enrollment_row = cursor.fetchone()
        enrollment = dict(enrollment_row) if enrollment_row else None
        completed_lessons = json.loads(enrollment["completed_lessons"]) if enrollment and enrollment.get("completed_lessons") else []

        # Modules and Lessons
        cursor.execute("SELECT * FROM course_modules WHERE course_id = ? ORDER BY order_num ASC", (course_id,))
        modules = [dict(row) for row in cursor.fetchall()]
        
        all_lessons = []
        for m in modules:
            cursor.execute("SELECT * FROM course_lessons WHERE module_id = ? ORDER BY order_num ASC", (m["id"],))
            m["lessons"] = [dict(l) for l in cursor.fetchall()]
            all_lessons.extend(m["lessons"])

        # Current Lesson selection
        current_lesson = None
        if active_lesson:
            current_lesson = next((l for l in all_lessons if l["id"] == active_lesson), None)
        if not current_lesson and all_lessons:
            current_lesson = all_lessons[0]

        # Quizzes for this course
        cursor.execute("""
            SELECT q.*,
                   (SELECT COUNT(*) FROM quiz_questions WHERE quiz_id = q.id) as question_count,
                   (SELECT score FROM quiz_attempts WHERE quiz_id = q.id AND user_id = ? ORDER BY attempted_at DESC LIMIT 1) as last_score,
                   (SELECT percentage FROM quiz_attempts WHERE quiz_id = q.id AND user_id = ? ORDER BY attempted_at DESC LIMIT 1) as last_percentage,
                   (SELECT is_passed FROM quiz_attempts WHERE quiz_id = q.id AND user_id = ? ORDER BY attempted_at DESC LIMIT 1) as is_passed,
                   (SELECT id FROM quiz_attempts WHERE quiz_id = q.id AND user_id = ? ORDER BY attempted_at DESC LIMIT 1) as last_attempt_id
            FROM quizzes q
            WHERE q.course_id = ? AND q.is_active = 1
        """, (user["id"], user["id"], user["id"], user["id"], course_id))
        quizzes = [dict(row) for row in cursor.fetchall()]

        # Check if Certificate already earned
        cursor.execute("SELECT * FROM certificates WHERE user_id = ? AND course_id = ?", (user["id"], course_id))
        cert = cursor.fetchone()
        certificate = dict(cert) if cert else None

        # Existing Feedback
        cursor.execute("SELECT * FROM course_feedback WHERE user_id = ? AND course_id = ?", (user["id"], course_id))
        fb = cursor.fetchone()
        feedback = dict(fb) if fb else None

        # Trainer Library items in same category
        cursor.execute("SELECT * FROM trainer_library WHERE category = ? LIMIT 3", (course["domain"],))
        resources = [dict(row) for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="trainee/course_detail.html", context={
        "request": request,
        "user": user,
        "course": course,
        "enrollment": enrollment,
        "modules": modules,
        "current_lesson": current_lesson,
        "completed_lessons": completed_lessons,
        "quizzes": quizzes,
        "certificate": certificate,
        "feedback": feedback,
        "resources": resources
    })

@router.post("/lesson/{lesson_id}/toggle")
def toggle_lesson_complete(request: Request, lesson_id: int):
    user = require_auth(request, allowed_roles=["trainee", "admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT course_id FROM course_lessons WHERE id = ?", (lesson_id,))
        lesson = cursor.fetchone()
        if not lesson:
            return JSONResponse({"error": "Lesson not found"}, status_code=404)
        course_id = lesson["course_id"]

        cursor.execute("SELECT id, completed_lessons FROM enrollments WHERE user_id = ? AND course_id = ?", (user["id"], course_id))
        enrollment = cursor.fetchone()
        if not enrollment:
            return JSONResponse({"error": "Not enrolled"}, status_code=400)

        completed = json.loads(enrollment["completed_lessons"] or "[]")
        if lesson_id in completed:
            completed.remove(lesson_id)
        else:
            completed.append(lesson_id)

        # Count total lessons
        cursor.execute("SELECT COUNT(*) FROM course_lessons WHERE course_id = ?", (course_id,))
        total_lessons = cursor.fetchone()[0]
        progress = int((len(completed) / max(1, total_lessons)) * 100)
        progress = min(100, progress)
        status_val = "completed" if progress >= 100 else "in_progress"
        completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if status_val == "completed" else None

        cursor.execute("""
            UPDATE enrollments
            SET completed_lessons = ?, progress_percent = ?, status = ?, completed_at = ?
            WHERE id = ?
        """, (json.dumps(completed), progress, status_val, completed_at, enrollment["id"]))

    return JSONResponse({
        "success": True,
        "progress_percent": progress,
        "is_completed": (lesson_id in completed),
        "status": status_val
    })

@router.get("/assessment/{quiz_id}", response_class=HTMLResponse)
def take_assessment_page(request: Request, quiz_id: int):
    user = require_auth(request, allowed_roles=["trainee", "admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT q.*, c.title as course_title, c.code as course_code
            FROM quizzes q
            JOIN courses c ON c.id = q.course_id
            WHERE q.id = ? AND q.is_active = 1
        """, (quiz_id,))
        quiz = cursor.fetchone()
        if not quiz:
            raise HTTPException(status_code=404, detail="Assessment not found or inactive")
        quiz = dict(quiz)

        # Fetch questions
        cursor.execute("""
            SELECT id, question_text, option_a, option_b, option_c, option_d, marks
            FROM quiz_questions
            WHERE quiz_id = ?
            ORDER BY id ASC
        """, (quiz_id,))
        questions = [dict(row) for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="trainee/assessment.html", context={
        "request": request,
        "user": user,
        "quiz": quiz,
        "questions": questions
    })

@router.post("/assessment/{quiz_id}/submit")
async def submit_assessment(request: Request, quiz_id: int):
    user = require_auth(request, allowed_roles=["trainee", "admin"])
    form_data = await request.form()
    
    user_answers = {}
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
        quiz = cursor.fetchone()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        quiz = dict(quiz)
        course_id = quiz["course_id"]

        cursor.execute("SELECT id, correct_option, marks FROM quiz_questions WHERE quiz_id = ?", (quiz_id,))
        questions = [dict(row) for row in cursor.fetchall()]

        total_marks = 0
        score = 0
        for q in questions:
            q_id_str = str(q["id"])
            ans = form_data.get(f"question_{q_id_str}")
            user_answers[q_id_str] = ans
            total_marks += q.get("marks", 1)
            if ans and ans.strip().upper() == q["correct_option"].strip().upper():
                score += q.get("marks", 1)

        percentage = round((score / max(1, total_marks)) * 100.0, 1)
        is_passed = 1 if percentage >= quiz.get("pass_percentage", 70) else 0

        # Save Attempt
        cursor.execute("""
            INSERT INTO quiz_attempts (quiz_id, user_id, course_id, score, total_marks, percentage, is_passed, user_answers)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (quiz_id, user["id"], course_id, score, total_marks, percentage, is_passed, json.dumps(user_answers)))
        attempt_id = cursor.lastrowid

        # If passed, issue or update Certificate
        if is_passed:
            cursor.execute("SELECT id, certificate_id FROM certificates WHERE user_id = ? AND course_id = ?", (user["id"], course_id))
            existing_cert = cursor.fetchone()
            if not existing_cert:
                cert_id = generate_certificate_id()
                grade = calculate_grade(percentage)
                v_url = f"/verify/certificate/{cert_id}"
                qr_data = f"MoES/IMD CAPACITY CONNECT | Certificate ID: {cert_id} | Recipient: {user['full_name']} | Course ID: {course_id} | Score: {percentage}% | Grade: {grade} | Verified by MoES Training Directorate"
                
                cursor.execute("""
                    INSERT INTO certificates (certificate_id, user_id, course_id, issue_date, grade, score_percentage, qr_data, verification_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (cert_id, user["id"], course_id, date.today().strftime('%Y-%m-%d'), grade, percentage, qr_data, v_url))

            # Mark course enrollment as 100% completed
            cursor.execute("""
                UPDATE enrollments
                SET progress_percent = 100, status = 'completed', completed_at = ?
                WHERE user_id = ? AND course_id = ?
            """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user["id"], course_id))

    return RedirectResponse(url=f"/trainee/assessment/result/{attempt_id}", status_code=303)

@router.get("/assessment/result/{attempt_id}", response_class=HTMLResponse)
def assessment_result_page(request: Request, attempt_id: int):
    user = require_auth(request, allowed_roles=["trainee", "admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT qa.*, q.title as quiz_title, q.pass_percentage, q.duration_mins,
                   c.id as course_id, c.title as course_title, c.code as course_code
            FROM quiz_attempts qa
            JOIN quizzes q ON q.id = qa.quiz_id
            JOIN courses c ON c.id = qa.course_id
            WHERE qa.id = ? AND qa.user_id = ?
        """, (attempt_id, user["id"]))
        attempt = cursor.fetchone()
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt record not found")
        attempt = dict(attempt)

        user_answers = json.loads(attempt["user_answers"] or "{}")

        # Questions for review
        cursor.execute("""
            SELECT id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, marks
            FROM quiz_questions
            WHERE quiz_id = ?
            ORDER BY id ASC
        """, (attempt["quiz_id"],))
        questions = [dict(row) for row in cursor.fetchall()]

        for q in questions:
            q_id_str = str(q["id"])
            q["user_selected"] = user_answers.get(q_id_str)
            q["is_correct"] = (q["user_selected"] == q["correct_option"])

        # Certificate if available
        cursor.execute("SELECT * FROM certificates WHERE user_id = ? AND course_id = ?", (user["id"], attempt["course_id"]))
        cert_row = cursor.fetchone()
        certificate = dict(cert_row) if cert_row else None

    return templates.TemplateResponse(request=request, name="trainee/assessment_result.html", context={
        "request": request,
        "user": user,
        "attempt": attempt,
        "questions": questions,
        "certificate": certificate
    })

@router.get("/certificate/{cert_id}", response_class=HTMLResponse)
def view_certificate(request: Request, cert_id: str):
    user = require_auth(request, allowed_roles=["trainee", "admin", "trainer"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT cert.*, u.full_name as trainee_name, u.designation as trainee_designation,
                   u.department as trainee_department,
                   c.title as course_title, c.code as course_code, c.domain as course_domain,
                   c.duration_hours,
                   tr.full_name as trainer_name, tr.designation as trainer_designation
            FROM certificates cert
            JOIN users u ON u.id = cert.user_id
            JOIN courses c ON c.id = cert.course_id
            LEFT JOIN users tr ON tr.id = c.trainer_id
            WHERE cert.certificate_id = ?
        """, (cert_id.strip(),))
        cert = cursor.fetchone()
        if not cert:
            raise HTTPException(status_code=404, detail="Certificate not found")
        certificate = dict(cert)

    return templates.TemplateResponse(request=request, name="trainee/certificate.html", context={
        "request": request,
        "user": user,
        "certificate": certificate
    })

@router.post("/feedback/{course_id}")
def submit_course_feedback(
    request: Request,
    course_id: int,
    rating_content: int = Form(...),
    rating_trainer: int = Form(...),
    rating_overall: int = Form(...),
    comments: str = Form("")
):
    user = require_auth(request, allowed_roles=["trainee", "admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT trainer_id FROM courses WHERE id = ?", (course_id,))
        crs = cursor.fetchone()
        trainer_id = crs["trainer_id"] if crs else None

        cursor.execute("""
            INSERT INTO course_feedback (course_id, user_id, trainer_id, rating_content, rating_trainer, rating_overall, comments)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (course_id, user["id"], trainer_id, rating_content, rating_trainer, rating_overall, comments.strip()))

    return RedirectResponse(url=f"/trainee/courses/{course_id}?feedback_success=1", status_code=303)
