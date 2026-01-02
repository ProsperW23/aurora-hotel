from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
from werkzeug.security import check_password_hash, generate_password_hash
import os
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-me-aurora")

# ---- Configure your DB credentials here ----
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASS = "_Wechieee05"
DB_NAME = "aurora_hotel"

# -----------------------------
# DB Connection Helper
# -----------------------------
def get_db():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4'
    )

# -----------------------------
# Login Decorator
# -----------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            flash("Please log in first.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# -----------------------------
# Public Pages
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rooms')
def rooms():
    return render_template('rooms.html')

@app.route('/booking', methods=['GET','POST'])
def booking():
    room_type = request.args.get("type") or request.form.get("room_type")

    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, room_type, price FROM rooms WHERE status='available' ORDER BY id")
        rooms = cur.fetchall()
    finally:
        conn.close()

    confirm_message = None

    if request.method == 'POST':
        try:
            name = request.form.get('guest_name') or request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            room_id = request.form.get('room_id')
            guests = request.form.get('guests', 1)
            checkin = request.form.get('checkin') or request.form.get('check_in')
            checkout = request.form.get('checkout') or request.form.get('check_out')

            if not all([name, email, phone, room_id, guests, checkin, checkout]):
                flash("All fields are required.", "error")
                return redirect(url_for('booking'))

            if '@' not in email:
                flash("Please include '@' in your email address.", "error")
                return redirect(url_for('booking'))

            room_id = int(room_id)
            guests = int(guests)

            conn = get_db()
            try:
                cur = conn.cursor()
                cur.execute("SELECT price FROM rooms WHERE id=%s", (room_id,))
                room_data = cur.fetchone()
                room_price = room_data['price'] if room_data else 0

                nights = (datetime.strptime(checkout, "%Y-%m-%d") - datetime.strptime(checkin, "%Y-%m-%d")).days or 1
                total_price = room_price * guests * nights

                cur.execute("""
                    INSERT INTO bookings (name, email, phone, room_id, guests, check_in, check_out, total_price, status)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'pending')
                """, (name, email, phone, room_id, guests, checkin, checkout, total_price))
                conn.commit()
            finally:
                conn.close()

            confirm_message = f"Booking confirmed for {name}! Total ₦{total_price:,}"
            flash(confirm_message, "success")

        except ValueError:
            flash("Guests and Room ID must be numbers.", "error")
            return redirect(url_for('booking'))

        except pymysql.MySQLError as e:
            flash(f"Database error: {e}", "error")
            return redirect(url_for('booking'))

        except Exception as e:
            flash(f"Unexpected error: {e}", "error")
            return redirect(url_for('booking'))

    return render_template('bookings.html', rooms=rooms, selected_room_type=room_type, confirm_message=confirm_message)

# -----------------------------
# Authentication
# -----------------------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')  # email input
        password = request.form.get('password')

        if not username or '@' not in username:
            flash("Please include '@' in your email address.", "error")
            return redirect(url_for('login'))

        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email=%s", (username,))
            user = cur.fetchone()
        finally:
            conn.close()

        if not user:
            flash(f"User '{username}' not found.", "error")
        elif not check_password_hash(user['password_hash'], password):
            flash("Incorrect password.", "error")
        else:
            session['user'] = user['username']
            session['role'] = user['role']
            flash(f"Welcome, {user['username']}!", "success")
            return redirect(url_for('admin'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

# -----------------------------
# Admin Section
# -----------------------------
@app.route('/admin')
@login_required
def admin():
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, b.name, b.email, b.phone, r.room_type, b.check_in, b.check_out, b.status, b.total_price
            FROM bookings b 
            JOIN rooms r ON b.room_id = r.id 
            ORDER BY b.id DESC
        """)
        bookings = cur.fetchall()
    finally:
        conn.close()

    return render_template('admin.html', bookings=bookings)

@app.route('/admin/confirm/<int:booking_id>', methods=['POST'])
@login_required
def confirm_booking(booking_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE bookings SET status='confirmed' WHERE id=%s", (booking_id,))
        conn.commit()
    finally:
        conn.close()

    flash('Booking confirmed!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/checkout/<int:booking_id>', methods=['POST'])
@login_required
def checkout_booking(booking_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE bookings SET status='checked_out' WHERE id=%s", (booking_id,))
        conn.commit()
    finally:
        conn.close()

    flash('Guest checked out successfully!', 'success')
    return redirect(url_for('admin'))

# -----------------------------
# API for frontend JS
# -----------------------------
@app.route('/api/rooms')
def api_rooms():
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, room_type, price, status FROM rooms ORDER BY id")
        rooms = cur.fetchall()
    finally:
        conn.close()
    return {"rooms": rooms}

# -----------------------------
# Create/update admin user automatically
# -----------------------------
def ensure_admin():
    admin_username = "admin"
    admin_password = "admin123"
    admin_email = "admin@aurorahotel.com"
    admin_role = "admin"
    password_hash = generate_password_hash(admin_password)

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW COLUMNS FROM users LIKE 'email';")
            if cur.rowcount == 0:
                cur.execute("ALTER TABLE users ADD COLUMN email VARCHAR(150) UNIQUE;")

            cur.execute("""
                INSERT INTO users (username, password_hash, role, email)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE password_hash=%s, role=%s, email=%s
            """, (admin_username, password_hash, admin_role, admin_email,
                  password_hash, admin_role, admin_email))
            conn.commit()
            print(f"✅ Admin '{admin_username}' ready. Use password: '{admin_password}', email: '{admin_email}'")
    finally:
        conn.close()

# -----------------------------
# Run App
# -----------------------------
if __name__ == '__main__':
    ensure_admin()

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT DATABASE()")
        print("⚡ Flask is connected to DB:", cur.fetchone())
        cur.execute("SHOW TABLES;")
        print("Tables Flask sees:", cur.fetchall())
        cur.execute("SHOW COLUMNS FROM users;")
        print("Users table columns:", cur.fetchall())
    conn.close()

    app.run(debug=True)









# from flask import Flask, render_template, request, redirect, url_for, flash, session
# import pymysql
# from werkzeug.security import check_password_hash, generate_password_hash
# import os
# from functools import wraps
# from datetime import datetime

# app = Flask(__name__)
# app.secret_key = os.environ.get("FLASK_SECRET", "change-me-aurora")

# # ---- Configure your DB credentials here ----
# DB_HOST = "localhost"
# DB_PORT = 3306
# DB_USER = "root"
# DB_PASS = "_Wechieee05"
# DB_NAME = "aurora_hotel"

# # -----------------------------
# # DB Connection Helper
# # -----------------------------
# def get_db():
#     return pymysql.connect(
#         host=DB_HOST,
#         port=DB_PORT,
#         user=DB_USER,
#         password=DB_PASS,
#         db=DB_NAME,
#         cursorclass=pymysql.cursors.DictCursor,
#         charset='utf8mb4'
#     )

# # -----------------------------
# # Login Decorator
# # -----------------------------
# def login_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         if not session.get("user"):
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#     return decorated

# # -----------------------------
# # Public Pages
# # -----------------------------
# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/rooms')
# def rooms():
#     return render_template('rooms.html')

# @app.route('/booking', methods=['GET','POST'])
# def booking():
#     room_type = request.args.get("type") or request.form.get("room_type")

#     conn = get_db()
#     try:
#         cur = conn.cursor()
#         cur.execute("SELECT id, room_type, price FROM rooms WHERE status='available' ORDER BY id")
#         rooms = cur.fetchall()
#     finally:
#         conn.close()

#     confirm_message = None

#     if request.method == 'POST':
#         try:
#             name = request.form.get('guest_name') or request.form.get('name')
#             email = request.form.get('email')
#             phone = request.form.get('phone')
#             room_id = request.form.get('room_id')
#             guests = request.form.get('guests', 1)
#             checkin = request.form.get('checkin') or request.form.get('check_in')
#             checkout = request.form.get('checkout') or request.form.get('check_out')

#             if not all([name, email, phone, room_id, guests, checkin, checkout]):
#                 flash("All fields are required.", "error")
#                 return redirect(url_for('booking'))

#             room_id = int(room_id)
#             guests = int(guests)

#             conn = get_db()
#             try:
#                 cur = conn.cursor()
#                 cur.execute("SELECT price FROM rooms WHERE id=%s", (room_id,))
#                 room_data = cur.fetchone()
#                 room_price = room_data['price'] if room_data else 0

#                 nights = (datetime.strptime(checkout, "%Y-%m-%d") - datetime.strptime(checkin, "%Y-%m-%d")).days or 1
#                 total_price = room_price * guests * nights

#                 cur.execute("""
#                     INSERT INTO bookings (name, email, phone, room_id, guests, check_in, check_out, total_price, status)
#                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'pending')
#                 """, (name, email, phone, room_id, guests, checkin, checkout, total_price))
#                 conn.commit()
#             finally:
#                 conn.close()

#             confirm_message = f"Booking confirmed for {name}! Total ₦{total_price:,}"
#             flash(confirm_message, "success")

#         except ValueError:
#             flash("Guests and Room ID must be numbers.", "error")
#             return redirect(url_for('booking'))

#         except pymysql.MySQLError as e:
#             flash(f"Database error: {e}", "error")
#             return redirect(url_for('booking'))

#         except Exception as e:
#             flash(f"Unexpected error: {e}", "error")
#             return redirect(url_for('booking'))

#     return render_template('bookings.html', rooms=rooms, selected_room_type=room_type, confirm_message=confirm_message)

# # -----------------------------
# # Authentication
# # -----------------------------
# @app.route('/login', methods=['GET','POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')

#         conn = get_db()
#         try:
#             cur = conn.cursor()
#             cur.execute("SELECT * FROM users WHERE username=%s", (username,))
#             user = cur.fetchone()
#         finally:
#             conn.close()

#         if not user:
#             flash(f"User '{username}' not found.", "error")
#         elif not check_password_hash(user['password_hash'], password):
#             flash("Incorrect password.", "error")
#         else:
#             session['user'] = user['username']
#             session['role'] = user['role']
#             flash(f"Welcome, {user['username']}!", "success")
#             return redirect(url_for('admin'))

#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.clear()
#     flash('Logged out successfully', 'info')
#     return redirect(url_for('index'))

# # -----------------------------
# # Admin Section
# # -----------------------------
# @app.route('/admin')
# @login_required
# def admin():
#     conn = get_db()
#     try:
#         cur = conn.cursor()
#         cur.execute("""
#             SELECT b.id, b.name, b.email, b.phone, r.room_type, b.check_in, b.check_out, b.status, b.total_price
#             FROM bookings b 
#             JOIN rooms r ON b.room_id = r.id 
#             ORDER BY b.id DESC
#         """)
#         bookings = cur.fetchall()
#     finally:
#         conn.close()

#     return render_template('admin.html', bookings=bookings)

# @app.route('/admin/confirm/<int:booking_id>', methods=['POST'])
# @login_required
# def confirm_booking(booking_id):
#     conn = get_db()
#     try:
#         cur = conn.cursor()
#         cur.execute("UPDATE bookings SET status='confirmed' WHERE id=%s", (booking_id,))
#         conn.commit()
#     finally:
#         conn.close()

#     flash('Booking confirmed!', 'success')
#     return redirect(url_for('admin'))

# # -----------------------------
# # API for frontend JS
# # -----------------------------
# @app.route('/api/rooms')
# def api_rooms():
#     conn = get_db()
#     try:
#         cur = conn.cursor()
#         cur.execute("SELECT id, room_type, price, status FROM rooms ORDER BY id")
#         rooms = cur.fetchall()
#     finally:
#         conn.close()
#     return {"rooms": rooms}

# # -----------------------------
# # Create/update admin user automatically
# # -----------------------------
# def ensure_admin():
#     admin_username = "admin"
#     admin_password = "admin123"  # safe password without special chars
#     admin_role = "admin"
#     password_hash = generate_password_hash(admin_password)

#     conn = get_db()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 INSERT INTO users (username, password_hash, role)
#                 VALUES (%s, %s, %s)
#                 ON DUPLICATE KEY UPDATE password_hash=%s, role=%s
#             """, (admin_username, password_hash, admin_role, password_hash, admin_role))
#             conn.commit()
#             print(f"✅ Admin '{admin_username}' ready. Use password: '{admin_password}'")
#     finally:
#         conn.close()

# # -----------------------------
# # Run App
# # -----------------------------
# if __name__ == '__main__':
#     ensure_admin()  # <-- create/update admin automatically

#     # Debug DB connection info
#     conn = get_db()
#     with conn.cursor() as cur:
#         cur.execute("SELECT DATABASE()")
#         print("⚡ Flask is connected to DB:", cur.fetchone())
#         cur.execute("SHOW TABLES;")
#         print("Tables Flask sees:", cur.fetchall())
#         cur.execute("SHOW COLUMNS FROM users;")
#         print("Users table columns:", cur.fetchall())
#     conn.close()

#     app.run(debug=True)
