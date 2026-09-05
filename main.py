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
    try:
        init_db()
        seed_db()
        print("CAPACITY CONNECT Server database initialized and verified successfully.")
    except Exception as e:
        import traceback
        print(f"WARNING: Initial database sync encountered an issue: {e}", file=sys.stderr)
        traceback.print_exc()
    yield

app = FastAPI(
    title=PORTAL_NAME,
    description=f"{PORTAL_SUBTITLE} - {ORGANIZATION}, {DEPARTMENT}",
    version="1.0.0",
    lifespan=lifespan
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import sys
    import traceback
    err_trace = traceback.format_exc()
    print(f"ERROR on {request.method} {request.url.path}: {exc}\n{err_trace}", file=sys.stderr)
    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>System Notice - CAPACITY CONNECT</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-slate-900 text-slate-100 min-h-screen flex items-center justify-center p-4">
            <div class="max-w-xl w-full bg-slate-800 border border-slate-700 rounded-3xl p-8 shadow-2xl space-y-4">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-2xl bg-rose-500/20 text-rose-400 flex items-center justify-center font-bold text-lg">!</div>
                    <div>
                        <h2 class="text-lg font-bold text-white">CAPACITY CONNECT - Runtime Notice</h2>
                        <p class="text-xs text-slate-400">An unexpected exception was intercepted by the portal</p>
                    </div>
                </div>
                <div class="bg-slate-950 p-4 rounded-xl font-mono text-xs text-rose-300 overflow-x-auto border border-slate-800">
                    <strong>{type(exc).__name__}:</strong> {str(exc)}
                </div>
                <div class="pt-2 flex gap-3">
                    <a href="/" class="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold transition">Return to Home</a>
                    <a href="javascript:location.reload()" class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-xl text-xs font-bold transition">Retry Request</a>
                </div>
            </div>
        </body>
        </html>
        """,
        status_code=500
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