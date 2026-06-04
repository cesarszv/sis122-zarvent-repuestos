"""User access operations for login and password handling."""

import bcrypt
from typing import List, Optional, TypedDict, Union, cast

import mysql.connector

from zarvent_repuestos.database.connection import get_database_connection


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

    except mysql.connector.Error:
        connection.rollback()
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


def list_users() -> List[User]:
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = "SELECT id, username FROM users ORDER BY id"
        cursor.execute(query)
        return cast(List[User], cursor.fetchall())

    except mysql.connector.Error:
        return []

    finally:
        cursor.close()
        connection.close()


def get_user_by_id(user_id: int) -> Optional[User]:
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
        return cast(Optional[User], cursor.fetchone())

    except mysql.connector.Error:
        return None

    finally:
        cursor.close()
        connection.close()


def update_user(user_id: int, username: str, password: str) -> bool:
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "UPDATE users SET username = %s, password = %s WHERE id = %s"
    password_hashed = hash_password(password)

    try:
        cursor.execute(query, (username, password_hashed, user_id))
        connection.commit()
        return cursor.rowcount > 0

    except mysql.connector.Error:
        connection.rollback()
        return False

    finally:
        cursor.close()
        connection.close()


def delete_user(user_id: int) -> bool:
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "DELETE FROM users WHERE id = %s"

    try:
        cursor.execute(query, (user_id,))
        connection.commit()
        return cursor.rowcount > 0

    except mysql.connector.Error:
        connection.rollback()
        return False

    finally:
        cursor.close()
        connection.close()
