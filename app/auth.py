import hashlib
import secrets
import json
import base64
import time
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from app.config import SECRET_KEY, SESSION_COOKIE_NAME, SESSION_MAX_AGE
import sqlite3

def generate_salt() -> str:
    return secrets.token_hex(16)

def hash_password(password: str, salt: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    key = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt_bytes, 100000)
    return key.hex()

def verify_password(password: str, salt: str, hashed: str) -> bool:
    return hash_password(password, salt) == hashed

def create_session_token(user_id: int, email: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": int(time.time()) + SESSION_MAX_AGE
    }
    payload_json = json.dumps(payload, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode('utf-8')).decode('utf-8').rstrip('=')
    signature = hashlib.sha256(f"{payload_b64}.{SECRET_KEY}".encode('utf-8')).hexdigest()
    return f"{payload_b64}.{signature}"

def decode_session_token(token: str) -> Optional[Dict[str, Any]]:
    if not token or '.' not in token:
        return None
    try:
        parts = token.split('.')
        if len(parts) != 2:
            return None
        payload_b64, signature = parts
        expected_sig = hashlib.sha256(f"{payload_b64}.{SECRET_KEY}".encode('utf-8')).hexdigest()
        if not secrets.compare_digest(signature, expected_sig):
            return None
        
        pad_len = 4 - (len(payload_b64) % 4)
        if pad_len < 4:
            payload_b64 += '=' * pad_len
        
        payload_json = base64.urlsafe_b64decode(payload_b64.encode('utf-8')).decode('utf-8')
        payload = json.loads(payload_json)
        
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None

def get_current_user_from_request(request: Request) -> Optional[Dict[str, Any]]:
    from app.database import get_db
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        return None
        
    payload = decode_session_token(token)
    if not payload:
        return None
        
    user_id = payload.get("user_id")
    if not user_id:
        return None
        
    try:
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT id, email, full_name, role, status, designation, department,
                       qualifications, experience_years, skills, interests, bio, avatar_url, created_at
                FROM users WHERE id = ?
            """, (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return dict(row)
    except Exception:
        return None

def require_auth(request: Request, allowed_roles: Optional[list] = None) -> Dict[str, Any]:
    user = get_current_user_from_request(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": f"/auth/login?next={request.url.path}"}
        )
    if user.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending administrator approval or inactive."
        )
    if allowed_roles and user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this portal resource."
        )
    return user
