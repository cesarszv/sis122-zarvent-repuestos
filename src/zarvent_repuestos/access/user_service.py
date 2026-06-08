"""User access operations for login and password handling."""

import logging
from typing import Optional, TypedDict, Union, cast

import bcrypt
import mysql.connector

from zarvent_repuestos.database.connection import get_database_connection


logger = logging.getLogger(__name__)


class User(TypedDict):
    id: int
    username: str


class UserRow(User):
    password: Union[str, bytes]


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    password_hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return password_hashed.decode("utf-8")


def password_matches(password: str, password_hashed: Union[str, bytes]) -> bool:
    if isinstance(password_hashed, str):
        password_hashed = password_hashed.encode("utf-8")

    return bcrypt.checkpw(password.encode("utf-8"), password_hashed)


def create_user(username: str, password: str) -> bool:
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    password_hashed = hash_password(password)

    try:
        cursor.execute(query, (username, password_hashed))
        connection.commit()
        return True

    except mysql.connector.Error as err:
        connection.rollback()
        logger.error("Error al crear usuario: %s", err)
        return False

    finally:
        cursor.close()
        connection.close()


def authenticate_user(username: str, password: str) -> Optional[User]:
    connection = None
    cursor = None
    query = "SELECT id, username, password FROM users WHERE username = %s"

    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (username,))
        row = cursor.fetchone()

        if row is None:
            return None

        user = cast(UserRow, row)
        password_hashed = user["password"]

        if password_matches(password, password_hashed):
            return {
                "id": user["id"],
                "username": user["username"],
            }

        return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
