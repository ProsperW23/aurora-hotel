-- init_db.sql for Aurora Hotel
DROP DATABASE IF EXISTS aurora_hotel;
CREATE DATABASE aurora_hotel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aurora_hotel;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('admin','receptionist') DEFAULT 'receptionist'
);

CREATE TABLE rooms (
  id INT AUTO_INCREMENT PRIMARY KEY,
  room_type VARCHAR(100) NOT NULL,
  price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  status ENUM('available','booked') DEFAULT 'available'
);

CREATE TABLE bookings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200),
  email VARCHAR(200),
  phone VARCHAR(50),
  room_id INT,
  check_in DATE,
  check_out DATE,
  status ENUM('pending','confirmed') DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

INSERT INTO rooms (room_type, price, status) VALUES
 ('Single', 50.00, 'available'),
 ('Double', 80.00, 'available'),
 ('Suite', 150.00, 'available');

-- Insert default admin (username: admin, password: admin123)
INSERT INTO users (username, password, role)
VALUES (
    'admin',
    'pbkdf2:sha256:260000$T8P9qB87o7dGhiJY$6efc672a05b49f42f229f1c7d26eec5f4edb32ce5c6b5c7f1fbb34ad50fbf157',
    'admin'
);
