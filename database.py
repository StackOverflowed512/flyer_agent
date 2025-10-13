import sqlite3
import os

# --- Database Setup ---
# Creates a 'data' directory if it doesn't exist to store the database file.
if not os.path.exists('data'):
    os.makedirs('data')

DATABASE_URL = "data/customers.db"

def init_db():
    """Initializes the database and creates the 'customers' table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    # The table stores customer information gathered by the chatbot.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        location TEXT,
        email TEXT,
        whatsapp TEXT,
        business_requirement TEXT,
        suggested_product TEXT,
        flyer_preference TEXT
    )
    ''')
    conn.commit()
    conn.close()

def save_customer_data(data):
    """Saves a new customer's data to the database."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO customers (name, location, email, whatsapp, business_requirement, suggested_product, flyer_preference)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('location'),
        data.get('email'),
        data.get('whatsapp'),
        data.get('business_requirement'),
        data.get('suggested_product'),
        data.get('flyer_preference')
    ))
    conn.commit()
    conn.close()