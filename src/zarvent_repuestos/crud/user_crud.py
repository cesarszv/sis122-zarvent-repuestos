"""CRUD operations for the users table using parameterized SQL."""

import bcrypt
import mysql.connector
from typing import List, Optional

from zarvent_repuestos.database.connection import get_database_connection
from zarvent_repuestos.models.user import User


def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    password_bytes = password.encode("utf-8")
    password_hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return password_hashed.decode("utf-8")


def password_matches(password: str, password_hashed: str) -> bool:
    """Verifies a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hashed.encode("utf-8"))


def crear_usuario(username: str, password: str) -> bool:
    """Creates a new user record in the database."""
    conexion = get_database_connection()
    cursor = conexion.cursor()
    sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
    password_hashed = hash_password(password)

    try:
        cursor.execute(sql, (username, password_hashed))
        conexion.commit()
        print("✅ Usuario creado")
        return True
    except mysql.connector.Error as err:
        conexion.rollback()
        print("❌ Error:", err)
        return False
    finally:
        cursor.close()
        conexion.close()


def leer_usuarios() -> List[User]:
    """Retrieves all users from the database."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)
    sql = "SELECT id, username, password FROM users"
    usuarios = []

    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            usuarios.append(User(username=row["username"], password=row["password"], id=row["id"]))
    except mysql.connector.Error as err:
        print("❌ Error:", err)
    finally:
        cursor.close()
        conexion.close()
    return usuarios


def actualizar_usuario(user_id: int, username: str, password: str) -> bool:
    """Updates a user's details including a new hashed password."""
    conexion = get_database_connection()
    cursor = conexion.cursor()
    sql = "UPDATE users SET username=%s, password=%s WHERE id=%s"
    password_hashed = hash_password(password)

    try:
        cursor.execute(sql, (username, password_hashed, user_id))
        conexion.commit()
        print("🔄 Usuario actualizado")
        return cursor.rowcount > 0
    except mysql.connector.Error as err:
        conexion.rollback()
        print("❌ Error:", err)
        return False
    finally:
        cursor.close()
        conexion.close()


def eliminar_usuario(user_id: int) -> bool:
    """Deletes a user record by ID."""
    conexion = get_database_connection()
    cursor = conexion.cursor()
    sql = "DELETE FROM users WHERE id=%s"

    try:
        cursor.execute(sql, (user_id,))
        conexion.commit()
        print("🗑️ Usuario eliminado")
        return cursor.rowcount > 0
    except mysql.connector.Error as err:
        conexion.rollback()
        print("❌ Error:", err)
        return False
    finally:
        cursor.close()
        conexion.close()


def autenticar_usuario(username: str, password: str) -> Optional[User]:
    """Checks credentials and returns the User object if authenticated."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)
    sql = "SELECT id, username, password FROM users WHERE username = %s"

    try:
        cursor.execute(sql, (username,))
        row = cursor.fetchone()
        if row and password_matches(password, row["password"]):
            return User(username=row["username"], password=row["password"], id=row["id"])
    except mysql.connector.Error as err:
        print("❌ Error de autenticación:", err)
    finally:
        cursor.close()
        conexion.close()
    return None
