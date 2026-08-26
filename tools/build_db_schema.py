import os
import sqlite3

def write_db_file():
    with open("app/database.py", "w", encoding="utf-8") as f:
        f.write('''import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime, date, timedelta
from app.config import DATABASE_PATH
from app.auth import generate_salt, hash_password

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as db:
        cursor = db.cursor()
        
        # 1. Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('trainee', 'trainer', 'admin')),
                status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('pending_approval', 'active', 'rejected', 'suspended')),
                designation TEXT,
                department TEXT,
                qualifications TEXT,
                experience_years INTEGER DEFAULT 0,
                skills TEXT,
                interests TEXT,
                bio TEXT,
                avatar_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Courses Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                domain TEXT NOT NULL,
                level TEXT NOT NULL DEFAULT 'Intermediate',
                duration_hours INTEGER DEFAULT 20,
                description TEXT,
                trainer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                thumbnail_url TEXT,
                status TEXT DEFAULT 'published',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. Course Modules
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                order_num INTEGER DEFAULT 1,
                summary TEXT
            );
        """)

        # 4. Course Lessons
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER REFERENCES course_modules(id) ON DELETE CASCADE,
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                lesson_type TEXT NOT NULL DEFAULT 'video',
                content_url TEXT,
                duration_mins INTEGER DEFAULT 15,
                notes TEXT,
                order_num INTEGER DEFAULT 1
            );
        """)

        # 5. Enrollments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                progress_percent INTEGER DEFAULT 0,
                completed_lessons TEXT DEFAULT '[]',
                status TEXT DEFAULT 'in_progress',
                completed_at TIMESTAMP,
                UNIQUE(user_id, course_id)
            );
        """)

        # 6. Quizzes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                trainer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                duration_mins INTEGER DEFAULT 20,
                pass_percentage INTEGER DEFAULT 70,
                deadline TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 7. Quiz Questions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_option TEXT NOT NULL CHECK(correct_option IN ('A', 'B', 'C', 'D')),
                explanation TEXT,
                marks INTEGER DEFAULT 1
            );
        """)

        # 8. Quiz Attempts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                score INTEGER NOT NULL,
                total_marks INTEGER NOT NULL,
                percentage REAL NOT NULL,
                is_passed INTEGER NOT NULL,
                user_answers TEXT,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 9. Certificates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                certificate_id TEXT UNIQUE NOT NULL,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                issue_date DATE NOT NULL,
                grade TEXT NOT NULL DEFAULT 'Distinction',
                score_percentage REAL NOT NULL,
                qr_data TEXT NOT NULL,
                verification_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 10. Course Feedback
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                trainer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                rating_content INTEGER NOT NULL,
                rating_trainer INTEGER NOT NULL,
                rating_overall INTEGER NOT NULL,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 11. Trainer Library Resources
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trainer_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trainer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                category TEXT NOT NULL,
                file_url TEXT,
                file_size TEXT,
                description TEXT,
                downloads_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 12. Announcements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Announcement',
                priority TEXT NOT NULL DEFAULT 'Normal',
                published_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
''')

if __name__ == "__main__":
    write_db_file()
    print("app/database.py schema written successfully")
