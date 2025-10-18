"""
Create a test user for SkinAI
"""
import sys
sys.path.append('.')

from app.database import SessionLocal
from app import crud, schemas

def create_test_user():
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = crud.get_user_by_email(db, "test@skinai.com")
        if existing_user:
            print("✅ Test user already exists!")
            print(f"   Email: test@skinai.com")
            print(f"   Password: test1234")
            print(f"   Name: {existing_user.name}")
            return
        
        # Create test user
        user_data = schemas.UserCreate(
            email="test@skinai.com",
            name="Test User",
            password="test1234"
        )
        
        user = crud.create_user(db, user_data)
        print("✅ Test user created successfully!")
        print(f"   Email: {user.email}")
        print(f"   Password: test1234")
        print(f"   Name: {user.name}")
        print(f"   ID: {user.id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
