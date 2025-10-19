import requests
import json

# Test login first
login_url = "http://localhost:8000/api/auth/login"
login_data = {
    "username": "test@skinai.com",
    "password": "password123"
}

print("1. Testing login...")
try:
    response = requests.post(login_url, data=login_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"   ✅ Login successful!")
        print(f"   Token: {token[:50]}...")
        
        # Test section creation
        print("\n2. Testing section creation...")
        create_url = "http://localhost:8000/api/sections/create"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        section_data = {
            "section_name": "face issue",
            "description": "test description"
        }
        
        response = requests.post(create_url, headers=headers, json=section_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code != 200:
            print(f"   ❌ ERROR!")
    else:
        print(f"   ❌ Login failed: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")
