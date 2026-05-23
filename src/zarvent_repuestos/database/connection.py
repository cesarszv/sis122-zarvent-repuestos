"""MySQL connection helper for the application."""

import os

import mysql.connector
from dotenv import load_dotenv


def get_database_connection():
    load_dotenv()
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )
