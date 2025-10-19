import sqlite3

conn = sqlite3.connect('skinai.db')
cursor = conn.cursor()

schema = cursor.execute('PRAGMA table_info(users)').fetchall()
print("=== USERS TABLE SCHEMA ===")
for col in schema:
    col_id, name, type_, notnull, default, pk = col
    print(f"{name:20} {type_:15} NOT NULL={notnull}")

conn.close()
