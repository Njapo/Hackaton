from app.database import SessionLocal
from app import crud, auth

db = SessionLocal()

email = "test@skinai.com"
password = "password123"

print(f"=== TESTING LOGIN FLOW ===")
print(f"Email: {email}")
print(f"Password: {password}")

# Step 1: Get user by email
print("\n1. Getting user by email...")
user = crud.get_user_by_email(db, email)
if user:
    print(f"   ✅ User found: {user.email} (ID: {user.id})")
    print(f"   Password hash: {user.password_hash[:50]}...")
else:
    print(f"   ❌ User NOT found!")
    db.close()
    exit(1)

# Step 2: Verify password
print("\n2. Verifying password...")
try:
    result = auth.verify_password(password, user.password_hash)
    if result:
        print(f"   ✅ Password verification PASSED")
    else:
        print(f"   ❌ Password verification FAILED")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 3: Full authenticate_user
print("\n3. Testing authenticate_user()...")
authenticated = auth.authenticate_user(db, email, password)
if authenticated:
    print(f"   ✅ Authentication successful!")
    print(f"   User: {authenticated.email}")
else:
    print(f"   ❌ Authentication FAILED")

db.close()
