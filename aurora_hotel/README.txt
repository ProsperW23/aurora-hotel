Aurora Hotel - Final Integrated Project (preserved frontend)

Files included:
- app.py
- init_db.sql
- requirements.txt
- templates/ (your original HTML files preserved and wired)
- static/ (your CSS/JS/images preserved)
- README.txt

Default admin credentials (seeded in init_db.sql):
  username: admin
  password: adminpass

Important notes:
- rooms.html remains static (served at /rooms-static).
- Booking form (bookings.html) loads rooms from DB for dropdown and posts to /booking.
- Login uses your login.html and posts to /login.
- Admin page (admin.html) is protected and lists bookings from DB; confirm via button.
- Update FLASK_SECRET and DB env vars for production use.

How to run:
1. Import DB: mysql -u root -p < init_db.sql
2. Install deps: pip install -r requirements.txt
3. Set environment vars if needed: DB_HOST, DB_USER, DB_PASS, DB_NAME, FLASK_SECRET
4. Run: python app.py
5. Visit: http://127.0.0.1:5000/ (homepage) and http://127.0.0.1:5000/rooms-static (static rooms page)


-- 7) Update or insert admin user
-- (If admin exists already, this will update its password hash)
UPDATE users
SET password_hash = 'pbkdf2:sha256:600000$uSk2dtKe59JMiE7N$7a43976cc8707d789d1e314d144ae2d2fc079a3b4dc925e5be05d6f406207a5c',
    role = 'admin'
WHERE username = 'admin';

-- If admin doesn’t exist, insert it:
INSERT INTO users (username, password_hash, role)
SELECT 'admin','pbkdf2:sha256:600000$uSk2dtKe59JMiE7N$7a43976cc8707d789d1e314d144ae2d2fc079a3b4dc925e5be05d6f406207a5c','admin'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username='admin');