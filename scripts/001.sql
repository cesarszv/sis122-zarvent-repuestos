/*
el profe dijo:
comando de mysql minimos para empezar(ejecutar en MySQL shell o cliente)
consejo;crear un ususario mysql con permisos ilimitados para la app en vez de usar root
*/

CREATE DATABASE sis122_zarvent_repuestos;
USE sis122_zarvent_repuestos;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE,
  password VARCHAR(100)
);
