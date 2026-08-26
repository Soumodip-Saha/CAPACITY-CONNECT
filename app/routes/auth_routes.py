from fastapi import APIRouter, Request, Form, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.config import SESSION_COOKIE_NAME, SESSION_MAX_AGE
from app.auth import (
    generate_salt, hash_password, verify_password,
    create_session_token, get_current_user_from_request, require_auth
)
from app.database import get_db
from app.models import ProfileUpdateRequest

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, next: str = ""):
    user = get_current_user_from_request(request)
    if user:
        role = user.get("role", "trainee")
        if role == "admin":
            return RedirectResponse(url="/admin/dashboard", status_code=303)
        elif role == "trainer":
            return RedirectResponse(url="/trainer/dashboard", status_code=303)
        else:
            return RedirectResponse(url="/trainee/dashboard", status_code=303)
    return templates.TemplateResponse(request=request, name="auth/login.html", context={"request": request, "next": next, "error": None})

@router.post("/login")
def handle_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("")
):
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, email, password_hash, salt, full_name, role, status
            FROM users WHERE email = ?
        """, (email.strip().lower(),))
        user = cursor.fetchone()

        if not user or not verify_password(password, user["salt"], user["password_hash"]):
            return templates.TemplateResponse(request=request, name="auth/login.html", context={"request": request, "next": next, "error": "Invalid email or password. Please try again."},
                status_code=400
            )

        if user["status"] == "pending_approval":
            return templates.TemplateResponse(request=request, name="auth/login.html", context={"request": request, "next": next, "error": "Your registration is currently pending Administrator approval. You will receive access once approved."},
                status_code=403
            )
        elif user["status"] != "active":
            return templates.TemplateResponse(request=request, name="auth/login.html", context={"request": request, "next": next, "error": "Your account is inactive. Please contact the MoES Capacity Building Cell."},
                status_code=403
            )

        token = create_session_token(user["id"], user["email"], user["role"])
        
        target_url = next if next and not next.startswith("/auth") else None
        if not target_url:
            if user["role"] == "admin":
                target_url = "/admin/dashboard"
            elif user["role"] == "trainer":
                target_url = "/trainer/dashboard"
            else:
                target_url = "/trainee/dashboard"

        response = RedirectResponse(url=target_url, status_code=303)
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=token,
            max_age=SESSION_MAX_AGE,
            httponly=True,
            samesite="lax"
        )
        return response

@router.get("/demo-login/{role}")
def demo_quick_login(request: Request, role: str):
    email_map = {
        "admin": "admin@imd.gov.in",
        "trainer": "dr.m.sharma@imd.gov.in",
        "trainee": "trainee.verma@imd.gov.in"
    }
    target_email = email_map.get(role.lower())
    if not target_email:
        return RedirectResponse(url="/auth/login", status_code=303)

    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id, email, role, status FROM users WHERE email = ?", (target_email,))
        user = cursor.fetchone()
        if not user:
            return RedirectResponse(url="/auth/login", status_code=303)

        token = create_session_token(user["id"], user["email"], user["role"])
        redirect_map = {
            "admin": "/admin/dashboard",
            "trainer": "/trainer/dashboard",
            "trainee": "/trainee/dashboard"
        }
        target_url = redirect_map.get(user["role"], "/trainee/dashboard")
        
        response = RedirectResponse(url=target_url, status_code=303)
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=token,
            max_age=SESSION_MAX_AGE,
            httponly=True,
            samesite="lax"
        )
        return response

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="auth/register.html", context={"request": request, "error": None, "success": None})

@router.post("/register")
def handle_register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    role: str = Form("trainee"),
    designation: str = Form(""),
    department: str = Form(""),
    qualifications: str = Form(""),
    experience_years: int = Form(0),
    skills: str = Form(""),
    interests: str = Form(""),
    bio: str = Form("")
):
    role = role.lower()
    if role not in ["trainee", "trainer"]:
        role = "trainee"

    # Trainers require admin approval, trainees are activated immediately
    initial_status = "pending_approval" if role == "trainer" else "active"

    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email.strip().lower(),))
        if cursor.fetchone():
            return templates.TemplateResponse(request=request, name="auth/register.html", context={"request": request, "error": "An account with this email address already exists. Please login instead.", "success": None},
                status_code=400
            )

        salt = generate_salt()
        pwd_hash = hash_password(password, salt)

        cursor.execute("""
            INSERT INTO users (
                email, password_hash, salt, full_name, role, status,
                designation, department, qualifications, experience_years,
                skills, interests, bio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            email.strip().lower(), pwd_hash, salt, full_name.strip(), role, initial_status,
            designation.strip(), department.strip(), qualifications.strip(), experience_years,
            skills.strip(), interests.strip(), bio.strip()
        ))
        new_user_id = cursor.lastrowid

    if initial_status == "pending_approval":
        return templates.TemplateResponse(request=request, name="auth/register.html", context={
                "request": request,
                "error": None,
                "success": "Trainer registration submitted successfully! Your credentials have been forwarded to the MoES Training Directorate for administrative verification and approval."
            }
        )
    else:
        # Auto-login for trainee
        token = create_session_token(new_user_id, email.strip().lower(), role)
        response = RedirectResponse(url="/trainee/dashboard", status_code=303)
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=token,
            max_age=SESSION_MAX_AGE,
            httponly=True,
            samesite="lax"
        )
        return response

@router.get("/logout")
def handle_logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response
