import sqlite3

conn = sqlite3.connect('skinai.db')
cursor = conn.cursor()

# Check all tables
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("=== ALL TABLES ===")
for table in tables:
    print(f"  - {table[0]}")

# Check users table
print("\n=== USERS TABLE ===")
try:
    users = cursor.execute("SELECT id, email, full_name FROM users").fetchall()
    print(f"Total users: {len(users)}")
    for user in users:
        print(f"  ID: {user[0]}, Email: {user[1]}, Name: {user[2]}")
except Exception as e:
    print(f"Error: {e}")

# Check lesion_sections table
print("\n=== LESION_SECTIONS TABLE ===")
try:
    sections = cursor.execute("SELECT section_id, section_name, user_id FROM lesion_sections").fetchall()
    print(f"Total sections: {len(sections)}")
    for section in sections:
        print(f"  ID: {section[0]}, Name: {section[1]}, User: {section[2]}")
except Exception as e:
    print(f"Error: {e}")

conn.close()
