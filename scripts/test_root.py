# Buscamos testear si funciona mysql aunque sea con root

import mysql.connector

conexion = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="sis122_zarvent_repuestos",
)

cursor = conexion.cursor()
cursor.execute("SELECT DATABASE()")
database = cursor.fetchone()[0]

print(f"conectado correctamente a {database}")

cursor.close()
conexion.close()
