import sqlite3

conn = sqlite3.connect('skinai.db')
cursor = conn.cursor()

users = cursor.execute("SELECT id, email, password_hash, name FROM users").fetchall()
print(f"=== USERS ({len(users)}) ===")
for user in users:
    user_id, email, pwd_hash, name = user
    print(f"\nID: {user_id}")
    print(f"Email: {email}")
    print(f"Name: {name}")
    print(f"Password Hash: {pwd_hash[:50]}..." if pwd_hash else "Password Hash: NONE!")

# Test bcrypt verification
if users:
    import bcrypt
    email, pwd_hash = users[0][1], users[0][2]
    test_password = "password123"
    
    print(f"\n=== TESTING PASSWORD VERIFICATION ===")
    print(f"Testing password: {test_password}")
    print(f"Hash in DB: {pwd_hash[:50]}...")
    
    try:
        result = bcrypt.checkpw(test_password.encode('utf-8'), pwd_hash.encode('utf-8'))
        if result:
            print("✅ Password verification WORKS!")
        else:
            print("❌ Password verification FAILED - wrong password")
    except Exception as e:
        print(f"❌ Error during verification: {e}")

conn.close()
