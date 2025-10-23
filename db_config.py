import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",              # default for XAMPP
        password="",              # empty password in most XAMPP installs
        database="waste_to_treasure",
        port=3306                 # update if your MySQL uses 3307 or 3308
    )
