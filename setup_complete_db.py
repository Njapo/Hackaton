from app.database import engine
from app.models import Base, User, ChatMessage, LesionSection, History
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

print("📝 Creating all tables from models...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created!")

# Verify tables exist
import sqlite3
conn = sqlite3.connect('skinai.db')
cursor = conn.cursor()

tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("\n=== TABLES IN DATABASE ===")
for table in tables:
    print(f"  ✅ {table[0]}")

# Create a test user
from app.database import SessionLocal
db = SessionLocal()

# Check if test user exists
existing_user = db.query(User).filter(User.email == "test@skinai.com").first()
if not existing_user:
    print("\n📝 Creating test user (test@skinai.com / password123)...")
    test_user = User(
        email="test@skinai.com",
        full_name="Test User",
        hashed_password=pwd_context.hash("password123")
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    print(f"✅ Test user created with ID: {test_user.id}")
else:
    print(f"\n✅ Test user already exists with ID: {existing_user.id}")

db.close()
conn.close()

print("\n✅ Database is ready!")
