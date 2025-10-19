import sqlite3
import bcrypt

conn = sqlite3.connect('skinai.db')
cursor = conn.cursor()

# Check tables
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("=== TABLES ===")
for table in tables:
    print(f"  ✅ {table[0]}")

# Hash password using bcrypt directly
password = "password123"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Check if user exists
existing = cursor.execute("SELECT id, email FROM users WHERE email=?", ("test@skinai.com",)).fetchone()

if existing:
    print(f"\n✅ User already exists: {existing[1]} (ID: {existing[0]})")
else:
    # Insert test user
    cursor.execute("""
        INSERT INTO users (email, full_name, hashed_password)
        VALUES (?, ?, ?)
    """, ("test@skinai.com", "Test User", hashed))
    conn.commit()
    
    user_id = cursor.lastrowid
    print(f"\n✅ Created test user: test@skinai.com (ID: {user_id})")
    print(f"   Password: password123")

# Also create a test section for the user
user_id = cursor.execute("SELECT id FROM users WHERE email=?", ("test@skinai.com",)).fetchone()[0]
section_exists = cursor.execute(
    "SELECT section_id FROM lesion_sections WHERE section_id=?", 
    ("9ec6b1a6-0ce8-4979-a21f-c48887661b5e",)
).fetchone()

if section_exists:
    print(f"\n✅ Test section already exists: 9ec6b1a6-0ce8-4979-a21f-c48887661b5e")
else:
    cursor.execute("""
        INSERT INTO lesion_sections (section_id, section_name, section_description, user_id)
        VALUES (?, ?, ?, ?)
    """, ("9ec6b1a6-0ce8-4979-a21f-c48887661b5e", "Test Lesion", "Test section for uploads", user_id))
    conn.commit()
    print(f"\n✅ Created test section: 9ec6b1a6-0ce8-4979-a21f-c48887661b5e")

conn.close()
print("\n✅ Database ready for testing!")
