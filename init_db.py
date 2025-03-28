import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS resources (
    resource TEXT PRIMARY KEY,
    quantity INTEGER
)
''')

cursor.executemany("INSERT OR IGNORE INTO resources (resource, quantity) VALUES (?, ?)", [
    ("Water (liters)", 1000),
    ("Fertilizer (kg)", 50),
    ("Seeds (kg)", 50),
    ("Pesticides (liters)", 70),
    ("Labour (workers)", 60),
    ("Machinery (units)", 15)
])

conn.commit()
conn.close()

print("Database initialized successfully.")
