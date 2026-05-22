import bcrypt

from db import get_connection


def hash_password(password):
    password_bytes = password.encode("utf-8")
    password_hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return password_hashed.decode("utf-8")


def create_user(username, password_hashed):
    connection = get_connection()
    cursor = connection.cursor()
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    # (%s, %s) significa que MySQL recibira los valores aparte del texto SQL.


    # try: "intenta ejecutar esto, pero puede fallar"
    try:
        cursor.execute(query, (username, password_hashed,))
        connection.commit()
        return True

    # except "si algo falla, haz esto"
    except Exception:
        connection.rollback()
        return False

    # finally
    finally:
        cursor.close()
        connection.close()


def login(username, password):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT id, username, password FROM users WHERE username = %s"

    try:
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user is None:
            return None

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

    except Exception:
        return None

    finally:
        cursor.close()
        connection.close()


def read_user(user_id=None):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        if user_id is None:
            query = "SELECT id, username FROM users ORDER BY id"
            cursor.execute(query)
            return cursor.fetchall()

        query = "SELECT id, username FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()

    except Exception:
        if user_id is None:
            return []
        return None

    finally:
        cursor.close()
        connection.close()


def update_user(user_id, username, password_hashed):
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


def delete_user(user_id):
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

# APRENDIZAJES
# cursor es el objeto que se usa para enviar SQL a la base de datos
