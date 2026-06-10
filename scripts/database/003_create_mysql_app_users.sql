-- Create the MySQL user used by the Python application.
-- v1 refactor: includes CREATE VIEW / DROP / SHOW VIEW so the application can
-- create the academic analytical views (`vw_low_stock_parts`,
-- `vw_daily_sales_summary`) from `init_db.py`.

CREATE USER IF NOT EXISTS 'zarvent_app'@'localhost' IDENTIFIED BY 'change_me';
CREATE USER IF NOT EXISTS 'zarvent_app'@'%' IDENTIFIED BY 'change_me';

ALTER USER 'zarvent_app'@'localhost' IDENTIFIED BY 'change_me';
ALTER USER 'zarvent_app'@'%' IDENTIFIED BY 'change_me';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES,
      CREATE VIEW, DROP, SHOW VIEW
ON sis122_zarvent_repuestos.*
TO 'zarvent_app'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES,
      CREATE VIEW, DROP, SHOW VIEW
ON sis122_zarvent_repuestos.*
TO 'zarvent_app'@'%';

FLUSH PRIVILEGES;
