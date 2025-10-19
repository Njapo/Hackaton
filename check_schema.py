import sqlite3

conn = sqlite3.connect('skinai.db')
cursor = conn.cursor()
schema = cursor.execute('PRAGMA table_info(history)').fetchall()

print("\n=== HISTORY TABLE SCHEMA ===")
print(f"Total columns: {len(schema)}")
for col in schema:
    print(f"Column: {col}")
    col_id, name, type_, notnull, default, pk = col
    null_str = "NOT NULL" if notnull else "NULL OK"
    print(f"{name:20} {type_:15} {null_str}")

# Check specifically for gemini_response
gemini_col = [c for c in schema if c[1] == 'gemini_response']
if gemini_col:
    col = gemini_col[0]
    print(f"\n✅ gemini_response column: notnull={col[3]} (0=nullable, 1=not null)")
else:
    print("\n❌ gemini_response column not found!")

conn.close()
