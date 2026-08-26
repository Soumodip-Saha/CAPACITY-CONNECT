import os
import sys
from pathlib import Path
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from app.config import DATABASE_URL

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0" if os.getenv("RENDER") else "127.0.0.1")
    
    db_mode = "PostgreSQL (Production/Render)" if DATABASE_URL and ("postgres" in DATABASE_URL or "postgresql" in DATABASE_URL) else "SQLite (Local Fallback)"

    print("=" * 70)
    print("  CAPACITY CONNECT - MoES & IMD Digital Capacity Building Portal")
    print("=" * 70)
    print(f"  * Server URL:      http://{host}:{port}")
    print(f"  * Database Mode:   {db_mode}")
    print("  * Public Portal:   http://localhost:8000")
    print("  * Course Catalog:  http://localhost:8000/trainee/courses")
    print("  * Admin Console:   http://localhost:8000/admin/dashboard")
    print("  * 1-Click Login:   Use the '1-Click Demo Login' button on top header")
    print("=" * 70)
    print("  Demo Accounts:")
    print("  - Admin:   admin@imd.gov.in           (Password: Admin@123)")
    print("  - Trainer: dr.m.sharma@imd.gov.in     (Password: Trainer@123)")
    print("  - Trainee: trainee.verma@imd.gov.in   (Password: Trainee@123)")
    print("=" * 70)

    # In production on Render, reload is False; in development, reload is True
    reload = not bool(os.getenv("RENDER") or os.getenv("PRODUCTION"))
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
