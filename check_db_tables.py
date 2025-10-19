import sqlite3

conn = sqlite3.connect('skinai.db')
cursor = conn.cursor()

print("=== TABLES IN DATABASE ===")
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for table in tables:
    print(f"  - {table[0]}")

print("\n=== CHECKING LESION_SECTIONS ===")
try:
    schema = cursor.execute('PRAGMA table_info(lesion_sections)').fetchall()
    if schema:
        print(f"Columns ({len(schema)}):")
        for col in schema:
            print(f"  - {col[1]} ({col[2]})")
    else:
        print("  ❌ Table doesn't exist!")
except Exception as e:
    print(f"  ❌ Error: {e}")

conn.close()
