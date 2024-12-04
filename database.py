# database.py
import sqlite3
import random

def create_database():
    conn = sqlite3.connect('warehouse.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            ItemID INTEGER PRIMARY KEY,
            Row INTEGER,
            Col INTEGER,
            Quantity INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# database.py - Modify populate_database
def populate_database(rows, cols, start_point, end_point):
    conn = sqlite3.connect('warehouse.db')
    c = conn.cursor()
    c.execute('DELETE FROM items')  # Clear existing data
    
    # Initialize empty cells with NULL quantity
    for row in range(rows):
        for col in range(cols):
            item_id = row * cols + col + 1
            c.execute('INSERT INTO items (ItemID, Row, Col, Quantity) VALUES (?, ?, ?, NULL)',
                     (item_id, row, col))
    
    conn.commit()
    conn.close()

def get_item(row, col):
    conn = sqlite3.connect('warehouse.db')
    c = conn.cursor()
    c.execute('SELECT ItemID, Quantity FROM items WHERE Row = ? AND Col = ?', (row, col))
    item = c.fetchone()
    conn.close()
    return item

def get_item_by_id(item_id):
    conn = sqlite3.connect('warehouse.db')
    c = conn.cursor()
    c.execute('SELECT Row, Col, Quantity FROM items WHERE ItemID = ?', (item_id,))
    item = c.fetchone()
    conn.close()
    return item

def update_item_quantity(item_id, quantity):
    conn = sqlite3.connect('warehouse.db')
    c = conn.cursor()
    c.execute('UPDATE items SET Quantity = ? WHERE ItemID = ?', (quantity, item_id))
    conn.commit()
    conn.close()