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
    
    # Extract last code frame for debugging clarity
    tb = traceback.extract_tb(exc.__traceback__)
    last_frame = tb[-1] if tb else None
    frame_info = f"{Path(last_frame.filename).name}:{last_frame.lineno} in {last_frame.name}" if last_frame else "Unknown"

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
                <div class="bg-slate-950 p-4 rounded-xl font-mono text-xs text-rose-300 overflow-x-auto border border-slate-800 space-y-2">
                    <div><strong class="text-white">{type(exc).__name__}:</strong> {str(exc)}</div>
                    <div class="pt-2 border-t border-slate-800 text-[11px] text-slate-400">
                        <span class="text-slate-500">Route:</span> <code class="text-amber-400">{request.method} {request.url.path}</code><br>
                        <span class="text-slate-500">Source:</span> <code class="text-sky-400">{frame_info}</code>
                    </div>
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
    featured_courses = []
    announcements = []
    total_trainees = 0
    total_trainers = 0
    total_courses = 0
    total_certificates = 0
    
    try:
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
            r = cursor.fetchone()
            total_trainees = (r[0] if r else 0) or 0

            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'trainer' AND status = 'active'")
            r = cursor.fetchone()
            total_trainers = (r[0] if r else 0) or 0

            cursor.execute("SELECT COUNT(*) FROM courses WHERE status = 'published'")
            r = cursor.fetchone()
            total_courses = (r[0] if r else 0) or 0

            cursor.execute("SELECT COUNT(*) FROM certificates")
            r = cursor.fetchone()
            total_certificates = (r[0] if r else 0) or 0
    except Exception as e:
        import sys
        print(f"Notice: Homepage database fetch exception handled: {e}", file=sys.stderr)
        try:
            init_db()
            seed_db()
        except Exception:
            pass

    return templates.TemplateResponse(request=request, name="index.html", context={
        "request": request,
        "user": user,
        "featured_courses": featured_courses,
        "announcements": announcements,
        "stats": {
            "trainees": total_trainees + 180,
            "trainers": total_trainers + 35,
            "courses": total_courses or 20,
            "certificates": total_certificates + 240
        }
    })

@app.get("/bulletins", response_class=HTMLResponse)
def public_bulletins(request: Request, category: str = "", search: str = ""):
    user = get_current_user_from_request(request)
    announcements = []
    categories = []

    with get_db() as db:
        cursor = db.cursor()
        query = """
            SELECT a.*, u.full_name as author_name
            FROM announcements a
            LEFT JOIN users u ON u.id = a.published_by
            WHERE a.is_active = 1
        """
        params = []
        if category and category.strip().lower() not in ("", "all"):
            query += " AND LOWER(a.category) = LOWER(?)"
            params.append(category.strip())
        if search and search.strip():
            query += " AND (LOWER(a.title) LIKE ? OR LOWER(a.content) LIKE ?)"
            term = f"%{search.strip().lower()}%"
            params.extend([term, term])
        query += " ORDER BY a.created_at DESC"
        cursor.execute(query, tuple(params))
        
        for row in cursor.fetchall():
            d = dict(row)
            raw = d.get("created_at")
            if hasattr(raw, "strftime"):
                d["created_at_display"] = raw.strftime("%Y-%m-%d")
            elif raw:
                d["created_at_display"] = str(raw)[:10]
            else:
                d["created_at_display"] = "Recent"
            announcements.append(d)

        cursor.execute("SELECT DISTINCT category FROM announcements WHERE is_active = 1 ORDER BY category ASC")
        categories = [row[0] for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="bulletins.html", context={
        "request": request,
        "user": user,
        "announcements": announcements,
        "categories": categories,
        "selected_category": category,
        "search": search
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