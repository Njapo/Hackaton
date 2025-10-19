#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('/home/v-nikolozij/hackaton/skinai.db')
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(history)")
columns = cursor.fetchall()

print("History table schema:")
print("="*60)
for col in columns:
    cid, name, dtype, notnull, default, pk = col
    nullable = "NOT NULL" if notnull else "NULLABLE"
    print(f"{name:20} {dtype:15} {nullable}")
print("="*60)

# Check specifically for gemini_response
cursor.execute("PRAGMA table_info(history)")
for col in cursor.fetchall():
    if col[1] == 'gemini_response':
        print(f"\n gemini_response column:")
        print(f"  Type: {col[2]}")
        print(f"  NOT NULL: {bool(col[3])}")
        print(f"  Default: {col[4]}")

conn.close()
