from typing import Optional, List
from fastapi import APIRouter, Request, Form, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.auth import require_auth
from app.database import get_db
from app.services.analytics_service import get_admin_dashboard_stats
from app.services.competency_engine import calculate_trainer_competency

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    user = require_auth(request, allowed_roles=["admin"])
    stats = get_admin_dashboard_stats()

    with get_db() as db:
        cursor = db.cursor()
        
        # Recent Users
        cursor.execute("SELECT id, full_name, email, role, status, designation, department, created_at FROM users ORDER BY created_at DESC LIMIT 6")
        recent_users = [dict(row) for row in cursor.fetchall()]

        # Recent Certificates
        cursor.execute("""
            SELECT cert.*, u.full_name as trainee_name, c.title as course_title
            FROM certificates cert
            JOIN users u ON u.id = cert.user_id
            JOIN courses c ON c.id = cert.course_id
            ORDER BY cert.created_at DESC
            LIMIT 5
        """)
        recent_certs = [dict(row) for row in cursor.fetchall()]

        # Active Announcements
        cursor.execute("SELECT * FROM announcements ORDER BY created_at DESC LIMIT 4")
        announcements = [dict(row) for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="admin/dashboard.html", context={
        "request": request,
        "user": user,
        "stats": stats,
        "recent_users": recent_users,
        "recent_certs": recent_certs,
        "announcements": announcements
    })

@router.get("/users", response_class=HTMLResponse)
def manage_users(request: Request, role: str = "", status_filter: str = "", search: str = ""):
    user = require_auth(request, allowed_roles=["admin"])
    
    query = """
        SELECT id, email, full_name, role, status, designation, department,
               qualifications, experience_years, skills, created_at,
               (SELECT COUNT(*) FROM enrollments WHERE user_id = users.id) as enrollments_count,
               (SELECT COUNT(*) FROM certificates WHERE user_id = users.id) as certs_count,
               (SELECT COUNT(*) FROM courses WHERE trainer_id = users.id) as courses_taught
        FROM users
        WHERE 1=1
    """
    params = []

    if role:
        query += " AND role = ?"
        params.append(role)
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    if search:
        query += " AND (full_name LIKE ? OR email LIKE ? OR department LIKE ? OR skills LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])

    query += " ORDER BY CASE WHEN status = 'pending_approval' THEN 0 ELSE 1 END, created_at DESC"

    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(query, params)
        users_list = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'pending_approval'")
        res = cursor.fetchone()
        if isinstance(res, dict):
            pending_count = next(iter(res.values()), 0)
        else:
            pending_count = res[0] if res and res[0] is not None else 0

    return templates.TemplateResponse(request=request, name="admin/users.html", context={
        "request": request,
        "user": user,
        "users_list": users_list,
        "pending_count": pending_count,
        "selected_role": role,
        "selected_status": status_filter,
        "search": search
    })

@router.post("/users/{target_user_id}/approve")
def approve_user(request: Request, target_user_id: int):
    user = require_auth(request, allowed_roles=["admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("UPDATE users SET status = 'active' WHERE id = ?", (target_user_id,))

    return RedirectResponse(url="/admin/users?approved=1", status_code=303)

@router.post("/users/{target_user_id}/reject")
def reject_user(request: Request, target_user_id: int):
    user = require_auth(request, allowed_roles=["admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("UPDATE users SET status = 'rejected' WHERE id = ?", (target_user_id,))

    return RedirectResponse(url="/admin/users?rejected=1", status_code=303)

@router.post("/users/{target_user_id}/role")
def update_user_role(request: Request, target_user_id: int, new_role: str = Form(...)):
    user = require_auth(request, allowed_roles=["admin"])
    
    if new_role in ["trainee", "trainer", "admin"]:
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, target_user_id))

    return RedirectResponse(url="/admin/users?role_updated=1", status_code=303)

@router.post("/users/{target_user_id}/status")
def update_user_status(request: Request, target_user_id: int, new_status: str = Form(...)):
    user = require_auth(request, allowed_roles=["admin"])
    
    if new_status in ["active", "suspended", "pending_approval", "rejected"]:
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, target_user_id))

    return RedirectResponse(url="/admin/users?status_updated=1", status_code=303)

@router.get("/competency-map", response_class=HTMLResponse)
def competency_mapping_page(
    request: Request,
    subject: str = "Numerical Weather Prediction & Data Assimilation",
    domain: str = "",
    min_experience: int = 5
):
    user = require_auth(request, allowed_roles=["admin"])
    
    ranked_trainers = calculate_trainer_competency(
        subject=subject,
        domain=domain,
        required_skills=[],
        min_experience=min_experience
    )

    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT DISTINCT domain FROM courses")
        
        # FIXED: Dictionary safe extraction for domains list
        domains = [next(iter(row.values())) if isinstance(row, dict) else row[0] for row in cursor.fetchall()]

        # Pre-set suggestions
        preset_topics = [
            "Numerical Weather Prediction & Data Assimilation",
            "Doppler Weather Radar Severe Storm Nowcasting",
            "INSAT-3DR Satellite Product Interpretation",
            "Tropical Cyclone Track & Intensity Forecasting",
            "Operational Agrometeorological Advisory Services",
            "Seismological Network & Tsunami Warning Systems",
            "AI/ML Applications in Extreme Rainfall Modeling",
            "High Performance Computing for Atmospheric Sciences"
        ]

    return templates.TemplateResponse(request=request, name="admin/competency_map.html", context={
        "request": request,
        "user": user,
        "ranked_trainers": ranked_trainers,
        "subject": subject,
        "domain": domain,
        "min_experience": min_experience,
        "domains": domains,
        "preset_topics": preset_topics
    })

@router.get("/announcements", response_class=HTMLResponse)
def manage_announcements(request: Request):
    user = require_auth(request, allowed_roles=["admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT a.*, u.full_name as author_name
            FROM announcements a
            LEFT JOIN users u ON u.id = a.published_by
            ORDER BY a.created_at DESC
        """)
        announcements = [dict(row) for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="admin/announcements.html", context={
        "request": request,
        "user": user,
        "announcements": announcements
    })

@router.post("/announcements/create")
def create_announcement(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form("Announcement"),
    priority: str = Form("Normal")
):
    user = require_auth(request, allowed_roles=["admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO announcements (title, content, category, priority, published_by, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (title.strip(), content.strip(), category.strip(), priority.strip(), user["id"]))

    return RedirectResponse(url="/admin/announcements?published=1", status_code=303)

@router.post("/announcements/{announcement_id}/delete")
def delete_announcement(request: Request, announcement_id: int):
    user = require_auth(request, allowed_roles=["admin"])
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM announcements WHERE id = ?", (announcement_id,))

    return RedirectResponse(url="/admin/announcements?deleted=1", status_code=303)
