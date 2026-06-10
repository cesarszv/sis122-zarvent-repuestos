-- Init script para el contenedor MySQL de Zarvent Repuestos.
--
-- Se ejecuta automaticamente por el entrypoint oficial de la imagen
-- `mysql:8.4` la primera vez que se inicializa el volumen de datos
-- (es decir, cuando el volumen `zarvent_mysql_data` esta vacio).
--
-- El entrypoint oficial corre cualquier archivo `*.sql` (ordenado por
-- nombre) en `/docker-entrypoint-initdb.d/` con el cliente `mysql` y
-- las credenciales de `MYSQL_ROOT_USER`/`MYSQL_ROOT_PASSWORD`. Este
-- script se ejecuta DESPUES de que el entrypoint ya creo la base
-- (`MYSQL_DATABASE`) y el usuario app (`MYSQL_USER`).
--
-- El objetivo de este script es darle al usuario de la aplicacion
-- (`zarvent_app`) los GRANTs necesarios para que `init_db.py` pueda
-- crear tablas, alterarlas, crear vistas y dejarlas en un estado
-- consistente. El contenedor MySQL ya crea el usuario con
-- `MYSQL_USER`/`MYSQL_PASSWORD`, pero por defecto solo le da acceso
-- basico a `MYSQL_DATABASE`. Por eso forzamos GRANTs explicitos.
--
-- IMPORTANTE: los valores de usuario, password y base de datos que
-- aparecen hardcoded aca coinciden con los que se usan en
-- `docker-compose.yml`, en el `.env.example` de `presentation/` y en
-- el `.env` del repo. Si se cambian los defaults en uno, hay que
-- cambiarlos en todos.

-- Normaliza el password del usuario app, en caso de que el contenedor
-- haya sido recreado con un valor distinto al actual.
CREATE USER IF NOT EXISTS 'zarvent_app'@'localhost' IDENTIFIED BY 'change_me';
CREATE USER IF NOT EXISTS 'zarvent_app'@'%'         IDENTIFIED BY 'change_me';
ALTER  USER        'zarvent_app'@'localhost' IDENTIFIED BY 'change_me';
ALTER  USER        'zarvent_app'@'%'         IDENTIFIED BY 'change_me';

-- GRANTs completos sobre la base de la app. Esto replica lo que hace
-- `scripts/database/003_create_mysql_app_users.sql` en la instalacion
-- local de Ubuntu.
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES,
      CREATE VIEW, DROP, SHOW VIEW
ON `sis122_zarvent_repuestos`.* TO 'zarvent_app'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES,
      CREATE VIEW, DROP, SHOW VIEW
ON `sis122_zarvent_repuestos`.* TO 'zarvent_app'@'%';

FLUSH PRIVILEGES;
