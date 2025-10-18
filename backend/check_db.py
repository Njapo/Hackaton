from app.database import SessionLocal
from app.crud import get_users

db = SessionLocal()
users = get_users(db)
print(f"\n📊 Database Status:")
print(f"   Total users: {len(users)}")
for u in users:
    print(f"   - {u.name} ({u.email}) - ID: {u.id}")
db.close()
