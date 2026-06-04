-- Create the MySQL user used by the Python application.

CREATE USER IF NOT EXISTS 'zarvent_app'@'localhost' IDENTIFIED BY 'change_me';
CREATE USER IF NOT EXISTS 'zarvent_app'@'%' IDENTIFIED BY 'change_me';

GRANT SELECT, INSERT, UPDATE, DELETE
ON sis122_zarvent_repuestos.*
TO 'zarvent_app'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE
ON sis122_zarvent_repuestos.*
TO 'zarvent_app'@'%';

FLUSH PRIVILEGES;
