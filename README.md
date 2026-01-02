Aurora Hotel – Hotel Management System

Aurora Hotel is a modern web-based hotel management system designed for seamless management of bookings, rooms, and guest records.
It helps hotel staff manage reservations efficiently, track room availability, and enhance overall guest experience.

Features

Room listing and availability tracking

Booking and reservation management

Guest record organization

Clean, responsive, and user-friendly interface

Dashboard for quick insights into hotel operations


Screenshots
<img width="1365" height="646" alt="Screenshot 2025-09-16 000736" src="https://github.com/user-attachments/assets/3425c314-d082-42ac-9b1e-649f542155bb" />
<img width="1365" height="468" alt="Screenshot 2025-09-16 001045" src="https://github.com/user-attachments/assets/04364c8b-1720-4d40-841b-d5fab4f13412" />
<img width="1346" height="492" alt="Screenshot 2025-09-16 001424" src="https://github.com/user-attachments/assets/448a3ac8-a7fa-4262-8483-8d81325b79b3" />
<img width="1365" height="622" alt="Screenshot 2025-09-16 001843" src="https://github.com/user-attachments/assets/45859315-f49c-4165-9277-ebc6d7a809e1" />



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
