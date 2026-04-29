# Same database connection
import mysql.connector
DB = {'host': 'localhost', 'database': 'tigerex'}
def connect():
    return mysql.connector.connect(**DB)
