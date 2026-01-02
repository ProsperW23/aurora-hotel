import pymysql
from werkzeug.security import generate_password_hash

# --- DB connection settings (same as your app.py) ---
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"   # change if needed
DB_PASS = "_Wechieee05"   # your MySQL password
DB_NAME = "aurora_hotel"  # your DB name

# --- User credentials (edit these each time you run the script) ---
username = input("Enter username: ").strip()
password = input("Enter password: ").strip()
role = input("Enter role (admin/receptionist): ").strip()

# --- Generate password hash ---
password_hash = generate_password_hash(password)

# --- Connect to DB ---
conn = pymysql.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASS,
    db=DB_NAME,
    cursorclass=pymysql.cursors.DictCursor,
    charset='utf8mb4'
)

try:
    with conn.cursor() as cur:
        # Insert or update user
        cur.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE password_hash=%s, role=%s
        """, (username, password_hash, role, password_hash, role))
        conn.commit()
        print(f"✅ User '{username}' created/updated successfully with role '{role}'")
finally:
    conn.close()
