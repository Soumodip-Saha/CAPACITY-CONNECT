import sys
import os
sys.path.insert(0, os.path.abspath("."))

from app.database import get_db

with get_db() as db:
    cursor = db.cursor()
    cursor.execute("SELECT id, code, title FROM courses")
    rows = cursor.fetchall()
    print(f"Current courses count: {len(rows)}")
    for r in rows:
        print(f" - {r[1]}: {r[2]}")
