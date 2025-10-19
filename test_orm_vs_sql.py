from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Raw SQL query
    result = conn.execute(text("SELECT * FROM users WHERE email = :email"), {"email": "test@skinai.com"})
    users = result.fetchall()
    
    print(f"=== RAW SQL QUERY ===")
    print(f"Found {len(users)} users")
    for user in users:
        print(f"User: {user}")

# Now try with ORM
from app.database import SessionLocal
from app.models import User

db = SessionLocal()
orm_user = db.query(User).filter(User.email == "test@skinai.com").first()

print(f"\n=== ORM QUERY ===")
if orm_user:
    print(f"✅ Found user: {orm_user.email}")
else:
    print(f"❌ User NOT found with ORM")
    
    # Try getting all users
    all_users = db.query(User).all()
    print(f"\nAll users in DB: {len(all_users)}")
    for u in all_users:
        print(f"  - {u.email}")

db.close()
