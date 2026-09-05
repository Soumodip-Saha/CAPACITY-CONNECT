import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory Paths
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# Database Configuration (PostgreSQL / SQLite fallback)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip()
    if DATABASE_URL.startswith("postgres://"):
        # Normalize Render's postgres:// URL scheme to postgresql://
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    if "sslmode=" not in DATABASE_URL and "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
        sep = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"

DATABASE_PATH = BASE_DIR / "capacity_connect.db"

# Uploads Configuration
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
(UPLOAD_DIR / "materials").mkdir(exist_ok=True)
(UPLOAD_DIR / "lectures").mkdir(exist_ok=True)
(UPLOAD_DIR / "profiles").mkdir(exist_ok=True)

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "moes-imd-capacity-connect-secret-key-2026-sih")
SESSION_COOKIE_NAME = "capacity_connect_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days in seconds

# Portal Identity
PORTAL_NAME = "CAPACITY CONNECT"
PORTAL_SUBTITLE = "Digital Capacity Building & Learning Management Portal"
ORGANIZATION = "Ministry of Earth Sciences (MoES)"
DEPARTMENT = "India Meteorological Department (IMD)"
MOTTO = "आदित्यात् जायते वृष्टिः (From the sun arises rain)"
