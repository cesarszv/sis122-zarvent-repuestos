"""MySQL connection helper for the application."""

import mysql.connector
from zarvent_repuestos.config.db_config import DB_CONFIG
from zarvent_repuestos.database.sql_trace import TracedConnection, is_sql_trace_enabled


def get_database_connection():
    """Returns a direct connection to MySQL based on the loaded DB_CONFIG."""
    conexion = mysql.connector.connect(**DB_CONFIG)
    if is_sql_trace_enabled():
        return TracedConnection(conexion)
    return conexion


def obtener_conexion():
    """Alias for get_database_connection with error logging to support the teacher's style."""
    try:
        conexion = get_database_connection()
        return conexion
    except mysql.connector.Error as err:
        print("❌ Error de conexión:", err)
        return None
