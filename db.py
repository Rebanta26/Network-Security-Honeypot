import mysql.connector

# shared DB config for countermeasures and main app
DB_CONFIG = dict(
    host='localhost',
    user='root',
    password='rebanta26',
    database='honeypot_db'
)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)