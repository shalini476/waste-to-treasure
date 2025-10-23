import mysql.connector
from mysql.connector import Error

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",          # update if you set password in XAMPP
        database="waste_to_treasure"
    )
