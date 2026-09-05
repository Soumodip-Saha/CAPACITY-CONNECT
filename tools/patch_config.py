import os

with open("app/config.py", "r", encoding="utf-8") as f:
    config_content = f.read()

# Update DATABASE_URL handling in app/config.py
old_db_conf = """DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # Normalize Render postgres:// URL scheme to postgresql://
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)"""

new_db_conf = """DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip()
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    if "sslmode=" not in DATABASE_URL and "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
        sep = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require""""

if old_db_conf in config_content:
    config_content = config_content.replace(old_db_conf, new_db_conf)
    with open("app/config.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    print("Updated app/config.py with sslmode=require handling")
else:
    print("Pattern not found in app/config.py, writing clean app/config.py")
