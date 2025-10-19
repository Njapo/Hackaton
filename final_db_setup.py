import sqlite3
import bcrypt

conn = sqlite3.connect('skinai.db')
cursor = conn.cursor()

print("📝 Creating all required tables...")

# Create users table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        name VARCHAR(100) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

# Create chat_messages table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        is_user BOOLEAN NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")

# Create lesion_sections table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS lesion_sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        section_id VARCHAR(36) UNIQUE NOT NULL,
        section_name VARCHAR(100) NOT NULL,
        section_description TEXT,
        user_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")

conn.commit()

# List all tables
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("\n=== ALL TABLES ===")
for table in tables:
    print(f"  ✅ {table[0]}")

# Create test user
password = "password123"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

existing = cursor.execute("SELECT id, email FROM users WHERE email=?", ("test@skinai.com",)).fetchone()

if existing:
    print(f"\n✅ Test user already exists: {existing[1]} (ID: {existing[0]})")
    user_id = existing[0]
else:
    cursor.execute("""
        INSERT INTO users (email, password_hash, name)
        VALUES (?, ?, ?)
    """, ("test@skinai.com", hashed, "Test User"))
    conn.commit()
    user_id = cursor.lastrowid
    print(f"\n✅ Created test user: test@skinai.com (ID: {user_id})")
    print(f"   Password: password123")

# Create test section
section_exists = cursor.execute(
    "SELECT section_id FROM lesion_sections WHERE section_id=?", 
    ("9ec6b1a6-0ce8-4979-a21f-c48887661b5e",)
).fetchone()

if section_exists:
    print(f"\n✅ Test section already exists")
else:
    cursor.execute("""
        INSERT INTO lesion_sections (section_id, section_name, section_description, user_id)
        VALUES (?, ?, ?, ?)
    """, ("9ec6b1a6-0ce8-4979-a21f-c48887661b5e", "Test Lesion", "Test section for uploads", user_id))
    conn.commit()
    print(f"\n✅ Created test section: 9ec6b1a6-0ce8-4979-a21f-c48887661b5e")

conn.close()
print("\n✅ Database fully ready!")
print("\n📋 Login credentials:")
print("   Email: test@skinai.com")
print("   Password: password123")
print("   Section ID: 9ec6b1a6-0ce8-4979-a21f-c48887661b5e")
