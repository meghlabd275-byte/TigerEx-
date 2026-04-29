#!/usr/bin/env python3
# Same database for macOS
DB_CONFIG = {
    'host': 'localhost',
    'database': 'tigerex',
    'user': 'root'
}
# Connects to shared backend
def get_connection():
    return psycopg2.connect(**DB_CONFIG)
