-- Create the login users table for the Flask prototype.

/*
Users table for the Flask login prototype.

The password column stores a bcrypt hash, not the plain text password.
*/

USE sis122_zarvent_repuestos;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(100) NOT NULL
);
