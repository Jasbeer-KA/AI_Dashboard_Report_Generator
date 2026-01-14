import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="app_user",
    password="Jasbeer1@",
    database="typing_class_db",
    port=3306
)

cursor = db.cursor()
cursor.execute("SHOW TABLES;")
for table in cursor.fetchall():
    print(table)


db.close()
from db import get_drill_type_name

print(get_drill_type_name(1))