# Comandos para la defensa

## Opción principal: SQL Trace visual en la app

Inicia Flask con el trazador SQL activado:

```bash
SQL_TRACE_ENABLED=1 uv run python -m flask --app zarvent_repuestos.web.app:app run --host 127.0.0.1 --port 5000 --no-debugger --no-reload
```

Abre la app:

```text
http://127.0.0.1:5000
```

Abre la vista de consultas en vivo:

```text
http://127.0.0.1:5000/sql-trace
```

Guion corto:

```text
Esta pantalla muestra las consultas SQL que ejecuta la aplicación con mysql-connector-python.
Cuando navego por dashboard, inventario o ventas, Flask llama a los módulos CRUD,
los módulos CRUD usan cursor.execute(...), y el trazador registra la consulta,
los parámetros, el estado y el tiempo de ejecución.
```

## Opción secundaria: log interno de MySQL

Entra a MySQL:

```bash
sudo mysql
```

Activa el general query log temporalmente:

```sql
SET GLOBAL log_output = 'TABLE';
SET GLOBAL general_log = 'ON';
```

Mira las consultas recientes del usuario de la app:

```bash
watch -n 1 "sudo mysql -e \"SELECT event_time, user_host, command_type, argument FROM mysql.general_log WHERE command_type = 'Query' AND user_host LIKE 'zarvent_app%' ORDER BY event_time DESC LIMIT 10\""
```

Apaga el general query log al terminar:

```sql
SET GLOBAL general_log = 'OFF';
```
