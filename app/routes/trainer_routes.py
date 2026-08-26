import json
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Request, Form, HTTPException, status, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.auth import require_auth
from app.database import get_db
from app.services.analytics_service import get_trainer_dashboard_stats

router = APIRouter(prefix="/trainer", tags=["trainer"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
def trainer_dashboard(request: Request):
    user = require_auth(request, allowed_roles=["trainer", "admin"])
    stats = get_trainer_dashboard_stats(user["id"])

    with get_db() as db:
        cursor = db.cursor()
        
        # Enrolled trainees across trainer courses
        cursor.execute("""
            SELECT e.id as enrollment_id, e.progress_percent, e.status, e.enrolled_at,
                   u.full_name as trainee_name, u.email as trainee_email, u.department as trainee_department,
                   c.title as course_title, c.code as course_code
            FROM enrollments e
            JOIN users u ON u.id = e.user_id
            JOIN courses c ON c.id = e.course_id
            WHERE c.trainer_id = ?
            ORDER BY e.enrolled_at DESC
            LIMIT 8
        """, (user["id"],))
        trainees = [dict(row) for row in cursor.fetchall()]

        # Active Quizzes created by this trainer
        cursor.execute("""
            SELECT q.*, c.title as course_title,
                   (SELECT COUNT(*) FROM quiz_questions WHERE quiz_id = q.id) as question_count,
                   (SELECT COUNT(*) FROM quiz_attempts WHERE quiz_id = q.id) as attempt_count,
                   (SELECT AVG(percentage) FROM quiz_attempts WHERE quiz_id = q.id) as avg_score
            FROM quizzes q
            JOIN courses c ON c.id = q.course_id
            WHERE q.trainer_id = ?
            ORDER BY q.created_at DESC
        """, (user["id"],))
        quizzes = [dict(row) for row in cursor.fetchall()]

        # Trainer Library items
        cursor.execute("SELECT * FROM trainer_library WHERE trainer_id = ? ORDER BY created_at DESC LIMIT 5", (user["id"],))
        resources = [dict(row) for row in cursor.fetchall()]

        # Feedback received
        cursor.execute("""
            SELECT f.*, u.full_name as trainee_name, c.title as course_title
            FROM course_feedback f
            JOIN users u ON u.id = f.user_id
            JOIN courses c ON c.id = f.course_id
            WHERE f.trainer_id = ?
            ORDER BY f.created_at DESC
            LIMIT 5
        """, (user["id"],))
        feedbacks = [dict(row) for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="trainer/dashboard.html", context={
        "request": request,
        "user": user,
        "stats": stats,
        "trainees": trainees,
        "quizzes": quizzes,
        "resources": resources,
        "feedbacks": feedbacks
    })

@router.get("/courses", response_class=HTMLResponse)
def trainer_courses(request: Request):
    user = require_auth(request, allowed_roles=["trainer", "admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT c.*,
                   (SELECT COUNT(*) FROM enrollments WHERE course_id = c.id) as enrollment_count,
                   (SELECT COUNT(*) FROM course_lessons WHERE course_id = c.id) as lesson_count,
                   (SELECT COUNT(*) FROM quizzes WHERE course_id = c.id) as quiz_count,
                   (SELECT AVG(rating_overall) FROM course_feedback WHERE course_id = c.id) as avg_rating
            FROM courses c
            WHERE c.trainer_id = ? OR ? = 'admin'
            ORDER BY c.created_at DESC
        """, (user["id"], user["role"]))
        courses = [dict(row) for row in cursor.fetchall()]

        # Domains list
        cursor.execute("SELECT DISTINCT domain FROM courses")
        domains = [row[0] for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="trainer/courses.html", context={
        "request": request,
        "user": user,
        "courses": courses,
        "domains": domains,
        "success": None,
        "error": None
    })

@router.post("/courses/create")
def create_course(
    request: Request,
    title: str = Form(...),
    code: str = Form(...),
    domain: str = Form(...),
    level: str = Form("Intermediate"),
    duration_hours: int = Form(20),
    description: str = Form(...)
):
    user = require_auth(request, allowed_roles=["trainer", "admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM courses WHERE code = ?", (code.strip().upper(),))
        if cursor.fetchone():
            return RedirectResponse(url="/trainer/courses?error=Course+code+already+exists", status_code=303)

        cursor.execute("""
            INSERT INTO courses (title, code, domain, level, duration_hours, description, trainer_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'published')
        """, (title.strip(), code.strip().upper(), domain.strip(), level, duration_hours, description.strip(), user["id"]))
        course_id = cursor.lastrowid

        # Create default module 1
        cursor.execute("""
            INSERT INTO course_modules (course_id, title, order_num, summary)
            VALUES (?, 'Module 1: Introduction & Foundational Concepts', 1, 'Core theoretical basis and fundamentals')
        """, (course_id,))
        m_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO course_lessons (module_id, course_id, title, lesson_type, content_url, duration_mins, notes, order_num)
            VALUES (?, ?, '1.1 Orientation and Program Objectives', 'video', 'https://www.youtube.com/embed/dQw4w9WgXcQ', 15, 'Overview of course roadmap.', 1)
        """, (m_id, course_id))

    return RedirectResponse(url=f"/trainer/courses/{course_id}/manage?success=Course+created+successfully", status_code=303)

@router.get("/courses/{course_id}/manage", response_class=HTMLResponse)
def manage_course_content(request: Request, course_id: int):
    user = require_auth(request, allowed_roles=["trainer", "admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        course = cursor.fetchone()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        course = dict(course)

        cursor.execute("SELECT * FROM course_modules WHERE course_id = ? ORDER BY order_num ASC", (course_id,))
        modules = [dict(row) for row in cursor.fetchall()]

        for m in modules:
            cursor.execute("SELECT * FROM course_lessons WHERE module_id = ? ORDER BY order_num ASC", (m["id"],))
            m["lessons"] = [dict(l) for l in cursor.fetchall()]

        cursor.execute("SELECT * FROM quizzes WHERE course_id = ?", (course_id,))
        quizzes = [dict(row) for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="trainer/course_manage.html", context={
        "request": request,
        "user": user,
        "course": course,
        "modules": modules,
        "quizzes": quizzes
    })

@router.post("/courses/{course_id}/modules/add")
def add_module(request: Request, course_id: int, title: str = Form(...), summary: str = Form("")):
    user = require_auth(request, allowed_roles=["trainer", "admin"])
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT COALESCE(MAX(order_num), 0) + 1 FROM course_modules WHERE course_id = ?", (course_id,))
        res = cursor.fetchone()
    next_order = next(iter(res.values())) if isinstance(res, dict) else (res[0] if res else 1)

        cursor.execute("""
            INSERT INTO course_modules (course_id, title, order_num, summary)
            VALUES (?, ?, ?, ?)
        """, (course_id, title.strip(), next_order, summary.strip()))

    return RedirectResponse(url=f"/trainer/courses/{course_id}/manage", status_code=303)

@router.post("/courses/{course_id}/lessons/add")
def add_lesson(
    request: Request,
    course_id: int,
    module_id: int = Form(...),
    title: str = Form(...),
    lesson_type: str = Form("video"),
    content_url: str = Form(""),
    duration_mins: int = Form(20),
    notes: str = Form("")
):
    user = require_auth(request, allowed_roles=["trainer", "admin"])
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT COALESCE(MAX(order_num), 0) + 1 FROM course_lessons WHERE module_id = ?", (module_id,))
        res = cursor.fetchone()
    next_order = next(iter(res.values())) if isinstance(res, dict) else (res[0] if res else 1)

        cursor.execute("""
            INSERT INTO course_lessons (module_id, course_id, title, lesson_type, content_url, duration_mins, notes, order_num)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (module_id, course_id, title.strip(), lesson_type, content_url.strip(), duration_mins, notes.strip(), next_order))

    return RedirectResponse(url=f"/trainer/courses/{course_id}/manage", status_code=303)

@router.get("/quiz/create", response_class=HTMLResponse)
def create_quiz_page(request: Request, course_id: Optional[int] = None):
    user = require_auth(request, allowed_roles=["trainer", "admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id, title, code, domain FROM courses WHERE trainer_id = ? OR ? = 'admin'", (user["id"], user["role"]))
        courses = [dict(row) for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="trainer/create_quiz.html", context={
        "request": request,
        "user": user,
        "courses": courses,
        "selected_course_id": course_id
    })

@router.post("/quiz/create")
async def handle_create_quiz(request: Request):
    user = require_auth(request, allowed_roles=["trainer", "admin"])
    form_data = await request.form()

    course_id = int(form_data.get("course_id"))
    title = form_data.get("title")
    subject = form_data.get("subject")
    duration_mins = int(form_data.get("duration_mins", 20))
    pass_percentage = int(form_data.get("pass_percentage", 70))
    deadline_days = int(form_data.get("deadline_days", 30))
    deadline = (datetime.now() + timedelta(days=deadline_days)).strftime('%Y-%m-%d %H:%M:%S')

    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO quizzes (course_id, trainer_id, title, subject, duration_mins, pass_percentage, deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (course_id, user["id"], title.strip(), subject.strip(), duration_mins, pass_percentage, deadline))
        quiz_id = cursor.lastrowid

        # Parse questions dynamically from form fields
        q_indices = set()
        for key in form_data.keys():
            if key.startswith("q_text_"):
                idx = key.replace("q_text_", "")
                q_indices.add(idx)

        for idx in sorted(list(q_indices), key=lambda x: int(x) if x.isdigit() else 0):
            q_text = form_data.get(f"q_text_{idx}")
            op_a = form_data.get(f"op_a_{idx}")
            op_b = form_data.get(f"op_b_{idx}")
            op_c = form_data.get(f"op_c_{idx}")
            op_d = form_data.get(f"op_d_{idx}")
            correct = form_data.get(f"correct_{idx}", "A").upper()
            expl = form_data.get(f"expl_{idx}", "")
            marks = int(form_data.get(f"marks_{idx}", 1))

            if q_text and op_a and op_b:
                cursor.execute("""
                    INSERT INTO quiz_questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, marks)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (quiz_id, q_text.strip(), op_a.strip(), op_b.strip(), (op_c or "").strip(), (op_d or "").strip(), correct, expl.strip(), marks))

    return RedirectResponse(url=f"/trainer/analytics?quiz_created=1", status_code=303)

@router.get("/library", response_class=HTMLResponse)
def trainer_library_page(request: Request):
    user = require_auth(request, allowed_roles=["trainer", "admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT l.*, u.full_name as trainer_name
            FROM trainer_library l
            JOIN users u ON u.id = l.trainer_id
            WHERE l.trainer_id = ? OR ? = 'admin'
            ORDER BY l.created_at DESC
        """, (user["id"], user["role"]))
        resources = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT domain FROM courses")
        domains = [row[0] for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="trainer/library.html", context={
        "request": request,
        "user": user,
        "resources": resources,
        "domains": domains
    })

@router.post("/library/upload")
def handle_library_upload(
    request: Request,
    title: str = Form(...),
    resource_type: str = Form(...),
    category: str = Form(...),
    file_url: str = Form(""),
    file_size: str = Form("12 MB"),
    description: str = Form("")
):
    user = require_auth(request, allowed_roles=["trainer", "admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO trainer_library (trainer_id, title, resource_type, category, file_url, file_size, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user["id"], title.strip(), resource_type, category, (file_url or "/static/docs/Meteorology_Material.pdf").strip(), file_size, description.strip()))

    return RedirectResponse(url="/trainer/library?upload_success=1", status_code=303)

@router.get("/analytics", response_class=HTMLResponse)
def trainer_analytics(request: Request):
    user = require_auth(request, allowed_roles=["trainer", "admin"])
    stats = get_trainer_dashboard_stats(user["id"])

    with get_db() as db:
        cursor = db.cursor()
        
        # All Trainee Attempts for trainer's quizzes
        cursor.execute("""
            SELECT qa.*, u.full_name as trainee_name, u.email as trainee_email, u.department as trainee_department,
                   q.title as quiz_title, c.title as course_title
            FROM quiz_attempts qa
            JOIN users u ON u.id = qa.user_id
            JOIN quizzes q ON q.id = qa.quiz_id
            JOIN courses c ON c.id = qa.course_id
            WHERE q.trainer_id = ? OR ? = 'admin'
            ORDER BY qa.attempted_at DESC
        """, (user["id"], user["role"]))
        attempts = [dict(row) for row in cursor.fetchall()]

        # Question level analytics
        cursor.execute("""
            SELECT qq.id, qq.question_text, qq.correct_option, q.title as quiz_title,
                   COUNT(qa.id) as total_answers
            FROM quiz_questions qq
            JOIN quizzes q ON q.id = qq.quiz_id
            LEFT JOIN quiz_attempts qa ON qa.quiz_id = q.id
            WHERE q.trainer_id = ? OR ? = 'admin'
            GROUP BY qq.id
            LIMIT 10
        """, (user["id"], user["role"]))
        question_stats = [dict(row) for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="trainer/analytics.html", context={
        "request": request,
        "user": user,
        "stats": stats,
        "attempts": attempts,
        "question_stats": question_stats
    })
