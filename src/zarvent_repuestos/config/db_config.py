"""Database configuration dictionary loaded from environment variables."""

import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "zarvent_app"),
    "password": os.getenv("DB_PASSWORD", "change_me"),
    "database": os.getenv("DB_NAME", "sis122_zarvent_repuestos"),
}
