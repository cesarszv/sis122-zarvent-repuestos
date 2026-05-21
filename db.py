# archivo para manejar la conexion a la base de datos
# el profesor recomendo leer las credenciales desde un .env en vez de escribirlas directo en el codigo

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# funcion para conectarse a la base de datos
def get_connection():
  return mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
  )

# aprendizajes:
# `os` es una libreria estandar de python para interactuar con el os, es decir, con el sistema operativo
# lo que viene de `dotenv` pertenece a `python-dotenv`; sirve para leer un archivo de entorno y cargar sus valores como variables de entorno
# load_dotenv hace que python cargue el contenido del .env
# el return hace que la funcion devuelva la sesion o el resultado de la conexion; asi, en otro archivo, una variable como `connection = get_connection()` recibe esa conexion
# este codigo permite definir una funcion reutilizable y evita repetir la conexion en cada archivo
# basicamente, esto es programacion modular: si manana cambia algo de la conexion, solo habria que modificar este archivo o el .env
