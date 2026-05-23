-- archivo para crear usuarios MySQL para la aplicacion

-- Crear usuario cesarszv
CREATE USER IF NOT EXISTS 'cesarszv'@'%' IDENTIFIED BY 'cesarszv';
GRANT ALL PRIVILEGES ON *.* TO 'cesarszv'@'%' WITH GRANT OPTION;

-- Crear usuario emanueljp
CREATE USER IF NOT EXISTS 'emanueljp'@'%' IDENTIFIED BY 'emanueljp';
GRANT ALL PRIVILEGES ON *.* TO 'emanueljp'@'%' WITH GRANT OPTION;

-- Aplicar cambios
FLUSH PRIVILEGES;
