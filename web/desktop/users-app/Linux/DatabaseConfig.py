#!/usr/bin/env python3
# Same database for Linux
DB_CONFIG = {
    'host': 'localhost', 
    'database': 'tigerex',
    'user': 'root'
}
# Unified backend
def get_connection():
    return psycopg2.connect(**DB_CONFIG)
