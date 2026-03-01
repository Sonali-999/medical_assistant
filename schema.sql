-- Use the correct database
CREATE DATABASE IF NOT EXISTS medical_assistant
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

USE medical_assistant;

-- Drop tables if they exist (in correct order for foreign keys)
DROP TABLE IF EXISTS chats;
DROP TABLE IF EXISTS users;

-- Users table
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chats table (linked to users)
CREATE TABLE chats (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  user_msg TEXT NOT NULL,
  bot_msg TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
