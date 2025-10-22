import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",       # default XAMPP user
        password="",       # leave blank unless you set one
        database="ecoloop_db" # your DB name
    )
