import sqlite3

conn = sqlite3.connect('skinai.db')
cursor = conn.cursor()

print("=== HISTORY_NEW TABLE SCHEMA ===")
schema = cursor.execute('PRAGMA table_info(history_new)').fetchall()
print(f"Total columns: {len(schema)}")
for col in schema:
    col_id, name, type_, notnull, default, pk = col
    null_str = "NOT NULL" if notnull else "NULL OK"
    print(f"{name:20} {type_:15} {null_str}")

# Check for gemini_response
gemini_col = [c for c in schema if c[1] == 'gemini_response']
if gemini_col:
    if gemini_col[0][3] == 0:
        print(f"\n✅ gemini_response is NULLABLE!")
    else:
        print(f"\n❌ gemini_response is NOT NULL")
else:
    print("\n❌ No gemini_response column")

# Rename history_new to history
print("\n📝 Renaming history_new to history...")
cursor.execute("DROP TABLE IF EXISTS history")
cursor.execute("ALTER TABLE history_new RENAME TO history")
conn.commit()
print("✅ Done!")

conn.close()
