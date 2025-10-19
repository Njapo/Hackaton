import sqlite3

conn = sqlite3.connect('skinai.db')
cursor = conn.cursor()

users = cursor.execute("SELECT id, email, name FROM users").fetchall()
print(f"=== ALL USERS IN DATABASE ({len(users)}) ===\n")
for user in users:
    print(f"ID: {user[0]}")
    print(f"Email: {user[1]}")
    print(f"Name: {user[2]}")
    print(f"---")

conn.close()
