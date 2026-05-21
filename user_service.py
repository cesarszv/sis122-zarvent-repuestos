from db import get_connection

def create_user(username, password_hashed):
    connection = get_connection()
    cursor = connection.cursor()
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    # (%s, %s) ---> significa que


    # try: "intenta ejecutar esto, pero puede fallar"
    try:
        cursor.execute(query, (username, password_hashed,))
        connection.commit()
        return True

    # except "si algo falla, haz esto"
    except Exception:
        return False

    # finally
    finally:
        cursor.close()
        connection.close()

# APRENDIZAJES
# cursor es el objeto que se usa para enviar SQL a la base de datos
