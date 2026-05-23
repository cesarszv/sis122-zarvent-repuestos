# Access module: users, passwords, and login operations.

import bcrypt
from typing import List, Optional, TypedDict, Union, cast

from zarvent_repuestos.infrastructure.mysql.connection import get_connection


class User(TypedDict):
    id: int
    username: str


class UserRow(User):
    password: Union[str, bytes]


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    password_hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return password_hashed.decode("utf-8")


def create_user(username: str, password_hashed: str) -> bool:
    connection = get_connection()
    cursor = connection.cursor()
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"

    try:
        cursor.execute(query, (username, password_hashed,))
        connection.commit()
        return True

    except Exception:
        connection.rollback()
        return False

    finally:
        cursor.close()
        connection.close()


def login(username: str, password: str) -> Optional[User]:
    connection = None
    cursor = None
    query = "SELECT id, username, password FROM users WHERE username = %s"

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (username,))
        row = cursor.fetchone()

        if row is None:
            return None

        user = cast(UserRow, row)
        password_hashed = user["password"]

        if isinstance(password_hashed, str):
            password_hashed = password_hashed.encode("utf-8")

        password_ok = bcrypt.checkpw(password.encode("utf-8"), password_hashed)

        if password_ok:
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


def read_user(user_id: Optional[int] = None) -> Union[List[User], Optional[User]]:
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        if user_id is None:
            query = "SELECT id, username FROM users ORDER BY id"
            cursor.execute(query)
            return cast(List[User], cursor.fetchall())

        query = "SELECT id, username FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        return cast(Optional[User], cursor.fetchone())

    except Exception:
        if user_id is None:
            return []
        return None

    finally:
        cursor.close()
        connection.close()


def update_user(user_id: int, username: str, password_hashed: str) -> bool:
    connection = get_connection()
    cursor = connection.cursor()
    query = "UPDATE users SET username = %s, password = %s WHERE id = %s"

    try:
        cursor.execute(query, (username, password_hashed, user_id,))
        connection.commit()
        return cursor.rowcount > 0

    except Exception:
        connection.rollback()
        return False

    finally:
        cursor.close()
        connection.close()


def delete_user(user_id: int) -> bool:
    connection = get_connection()
    cursor = connection.cursor()
    query = "DELETE FROM users WHERE id = %s"

    try:
        cursor.execute(query, (user_id,))
        connection.commit()
        return cursor.rowcount > 0

    except Exception:
        connection.rollback()
        return False

    finally:
        cursor.close()
        connection.close()
