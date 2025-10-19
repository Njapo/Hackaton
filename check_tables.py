import sqlite3

conn = sqlite3.connect('skinai.db')
cursor = conn.cursor()

# List all tables
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("=== ALL TABLES ===")
for table in tables:
    print(f"  - {table[0]}")

# Check history table
print("\n=== HISTORY TABLE INFO ===")
try:
    schema = cursor.execute('PRAGMA table_info(history)').fetchall()
    print(f"Columns: {len(schema)}")
    for col in schema:
        print(f"  {col}")
except Exception as e:
    print(f"Error: {e}")

conn.close()
