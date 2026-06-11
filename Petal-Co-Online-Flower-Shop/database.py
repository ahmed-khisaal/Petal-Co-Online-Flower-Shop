import sqlite3

"""
database.py — Run this once to initialise the Petal & Co database.
Usage: python database.py
"""

conn = sqlite3.connect("flowershop.db")
cur = conn.cursor()

cur.executescript("""
    -- Customers table with password hashing support & join timestamp
    CREATE TABLE IF NOT EXISTS customers (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name     TEXT NOT NULL,
        email    TEXT NOT NULL UNIQUE,
        phone    TEXT NOT NULL,
        address  TEXT NOT NULL,
        password TEXT NOT NULL,
        joined   TEXT DEFAULT (datetime('now'))
    );

    -- Orders table with customer FK and order status
    CREATE TABLE IF NOT EXISTS orders (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER REFERENCES customers(id),
        name        TEXT NOT NULL,
        flower      TEXT NOT NULL,
        quantity    INTEGER NOT NULL,
        total       INTEGER NOT NULL,
        status      TEXT DEFAULT 'Pending',
        order_date  TEXT NOT NULL
    );
""")

conn.commit()
conn.close()

print(" Database initialised successfully — flowershop.db")
print("   Tables: customers, orders")
