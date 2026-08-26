import os

with open("app/database.py", "w", encoding="utf-8") as f:
    f.write('''import os
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, date, timedelta
from app.config import DATABASE_PATH, DATABASE_URL
from app.auth import generate_salt, hash_password

try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

def is_postgres() -> bool:
    return bool(DATABASE_URL and ("postgres" in DATABASE_URL or "postgresql" in DATABASE_URL))

class PostgresCursorWrapper:
    def __init__(self, raw_cursor):
        self.cursor = raw_cursor
        self.lastrowid = None

    def _convert_query(self, query: str) -> str:
        return query.replace("?", "%s")

    def execute(self, query, params=None):
        pg_query = self._convert_query(query)
        is_insert = pg_query.strip().upper().startswith("INSERT INTO")
        has_returning = "RETURNING" in pg_query.upper()

        if is_insert and not has_returning:
            pg_query_with_ret = pg_query.rstrip(";") + " RETURNING id;"
            try:
                if params:
                    self.cursor.execute(pg_query_with_ret, params)
                else:
                    self.cursor.execute(pg_query_with_ret)
                res = self.cursor.fetchone()
                if res:
                    if isinstance(res, dict):
                        self.lastrowid = res.get("id")
                    elif isinstance(res, (tuple, list)):
                        self.lastrowid = res[0]
                    elif hasattr(res, "__getitem__"):
                        self.lastrowid = res["id"]
            except Exception:
                if params:
                    self.cursor.execute(pg_query, params)
                else:
                    self.cursor.execute(pg_query)
            return self
        else:
            if params:
                self.cursor.execute(pg_query, params)
            else:
                self.cursor.execute(pg_query)
            return self

    def executemany(self, query, seq_of_params):
        pg_query = self._convert_query(query)
        return self.cursor.executemany(pg_query, seq_of_params)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchmany(self, size=None):
        return self.cursor.fetchmany(size) if size else self.cursor.fetchmany()

    @property
    def rowcount(self):
        return self.cursor.rowcount

    def close(self):
        return self.cursor.close()

    def __iter__(self):
        return iter(self.cursor)

class PostgresConnectionWrapper:
    def __init__(self, raw_conn):
        self.conn = raw_conn

    def cursor(self):
        return PostgresCursorWrapper(self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor))

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def close(self):
        return self.conn.close()

@contextmanager
def get_db():
    if is_postgres():
        if not PSYCOPG2_AVAILABLE:
            raise RuntimeError("psycopg2-binary is required for PostgreSQL. Install with: pip install psycopg2-binary")
        conn = psycopg2.connect(DATABASE_URL)
        wrapper = PostgresConnectionWrapper(conn)
        try:
            yield wrapper
            wrapper.commit()
        except Exception:
            wrapper.rollback()
            raise
        finally:
            wrapper.close()
    else:
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
    use_pg = is_postgres()
    pk_type = "SERIAL PRIMARY KEY" if use_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    with get_db() as db:
        cursor = db.cursor()
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                id {pk_type},
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

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS courses (
                id {pk_type},
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

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS course_modules (
                id {pk_type},
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                order_num INTEGER DEFAULT 1,
                summary TEXT
            );
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS course_lessons (
                id {pk_type},
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

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS enrollments (
                id {pk_type},
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

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS quizzes (
                id {pk_type},
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

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id {pk_type},
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

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id {pk_type},
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

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS certificates (
                id {pk_type},
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

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS course_feedback (
                id {pk_type},
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

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS trainer_library (
                id {pk_type},
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

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS announcements (
                id {pk_type},
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

print("Part 1 of app/database.py written")
