import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import (
    PORTAL_NAME, PORTAL_SUBTITLE, ORGANIZATION, DEPARTMENT, MOTTO, BASE_DIR
)
from app.database import init_db, seed_db, get_db
from app.auth import get_current_user_from_request
from app.services.certificate_service import verify_certificate_by_id

from app.routes.auth_routes import router as auth_router
from app.routes.trainee_routes import router as trainee_router
from app.routes.trainer_routes import router as trainer_router
from app.routes.admin_routes import router as admin_router
from app.routes.api_routes import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize and seed database on startup
    init_db()
    seed_db()
    print("CAPACITY CONNECT Server initialized with SQLite database and seed data.")
    yield

app = FastAPI(
    title=PORTAL_NAME,
    description=f"{PORTAL_SUBTITLE} - {ORGANIZATION}, {DEPARTMENT}",
    version="1.0.0",
    lifespan=lifespan
)

# Mount Static & Uploads
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include Sub-Routers
app.include_router(auth_router)
app.include_router(trainee_router)
app.include_router(trainer_router)
app.include_router(admin_router)
app.include_router(api_router)

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def root_redirect():
    return RedirectResponse(url="/auth/login", status_code=303)
    
@app.get("/login", response_class=HTMLResponse)
def redirect_to_auth_login():
    return RedirectResponse(url="/auth/login", status_code=303)

@app.get("/", response_class=HTMLResponse)
def index_homepage(request: Request):
    user = get_current_user_from_request(request)
    
    with get_db() as db:
        cursor = db.cursor()
        
        # Featured courses
        cursor.execute("""
            SELECT c.*, u.full_name as trainer_name, u.designation as trainer_designation,
                   (SELECT COUNT(*) FROM enrollments WHERE course_id = c.id) as enrolled_count
            FROM courses c
            LEFT JOIN users u ON u.id = c.trainer_id
            WHERE c.status = 'published'
            ORDER BY c.id ASC
            LIMIT 6
        """)
        featured_courses = [dict(row) for row in cursor.fetchall()]

        # Active Announcements / Circulars
        cursor.execute("SELECT * FROM announcements WHERE is_active = 1 ORDER BY created_at DESC LIMIT 5")
        announcements = [dict(row) for row in cursor.fetchall()]

        # Key Portal Counters
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'trainee'")
        total_trainees = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'trainer' AND status = 'active'")
        total_trainers = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM courses WHERE status = 'published'")
        total_courses = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM certificates")
        total_certificates = cursor.fetchone()[0]

    return templates.TemplateResponse(request=request, name="index.html", context={
        "request": request,
        "user": user,
        "featured_courses": featured_courses,
        "announcements": announcements,
        "stats": {
            "trainees": total_trainees + 180,  # Include historical trained count
            "trainers": total_trainers + 35,
            "courses": total_courses,
            "certificates": total_certificates + 240
        }
    })

@app.get("/verify/certificate/{cert_id}", response_class=HTMLResponse)
def public_verify_certificate(request: Request, cert_id: str):
    user = get_current_user_from_request(request)
    cert = verify_certificate_by_id(cert_id)
    
    return templates.TemplateResponse(request=request, name="verify_certificate.html", context={
        "request": request,
        "user": user,
        "cert_id": cert_id,
        "certificate": cert,
        "is_valid": (cert is not None)
    })

@app.exception_handler(404)
def custom_404(request: Request, exc: HTTPException):
    user = get_current_user_from_request(request)
    return templates.TemplateResponse(request=request, name="base.html", context={
        "request": request,
        "user": user,
        "error_code": 404,
        "error_message": "The requested Capacity Building portal resource was not found."
    }, status_code=404)
@app.exception_handler(404)
def custom_404(request: Request, exc: HTTPException):
    user = get_current_user_from_request(request)
    # Change "base.html" to "404.html" so it actually shows an error message!
    return templates.TemplateResponse(request=request, name="404.html", context={
        "request": request,
        "user": user,
        "error_code": 404,
        "error_message": "The requested Capacity Building portal resource was not found."
    }, status_code=404)
