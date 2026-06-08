"""MySQL connection helper for the application."""

import logging

import mysql.connector
from zarvent_repuestos.config.db_config import DB_CONFIG
from zarvent_repuestos.database.sql_trace import TracedConnection, is_sql_trace_enabled


logger = logging.getLogger(__name__)


def get_database_connection():
    """Returns a direct connection to MySQL based on the loaded DB_CONFIG.

    When SQL tracing is enabled, the returned connection is a thin wrapper
    that records every executed statement into an in-memory ring buffer.
    """
    conexion = mysql.connector.connect(**DB_CONFIG)
    if is_sql_trace_enabled():
        return TracedConnection(conexion)
    return conexion
