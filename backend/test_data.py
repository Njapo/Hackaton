"""
test_data.py - Script to populate database with sample data for testing

Run this script to add test users, animals, and chat messages to your database.

Usage:
    python test_data.py
"""

import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app import crud, schemas
from app.auth import get_password_hash


def create_test_data():
    """Create sample data for testing."""
    
    # Initialize database
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        print("🌱 Creating test data...\n")
        
        # ============= Create Test Users =============
        print("👤 Creating users...")
        
        # Check if users already exist
        existing_user = crud.get_user_by_email(db, "john@example.com")
        if existing_user:
            print("   ⚠️  Users already exist. Skipping user creation.")
            user1 = existing_user
            user2 = crud.get_user_by_email(db, "jane@example.com")
        else:
            user1_data = schemas.UserCreate(
                email="john@example.com",
                name="John Doe",
                password="password123"
            )
            user1 = crud.create_user(db, user1_data)
            print(f"   ✅ Created user: {user1.name} ({user1.email})")
            
            user2_data = schemas.UserCreate(
                email="jane@example.com",
                name="Jane Smith",
                password="password123"
            )
            user2 = crud.create_user(db, user2_data)
            print(f"   ✅ Created user: {user2.name} ({user2.email})")
        
        # ============= Create Test Animals =============
        print("\n🐾 Creating animals...")
        
        # John's animals
        animals_to_create = [
            {
                "name": "Buddy",
                "species": "Dog",
                "breed": "Golden Retriever",
                "age": 3,
                "weight": 30.5,
                "icon_emoji": "🐕",
                "owner_id": user1.id
            },
            {
                "name": "Whiskers",
                "species": "Cat",
                "breed": "Persian",
                "age": 2,
                "weight": 4.5,
                "icon_emoji": "🐱",
                "owner_id": user1.id
            },
            {
                "name": "Charlie",
                "species": "Dog",
                "breed": "Beagle",
                "age": 5,
                "weight": 12.3,
                "icon_emoji": "🐶",
                "owner_id": user2.id
            },
            {
                "name": "Tweety",
                "species": "Bird",
                "breed": "Canary",
                "age": 1,
                "weight": 0.02,
                "icon_emoji": "🐦",
                "owner_id": user2.id
            }
        ]
        
        created_animals = []
        for animal_data in animals_to_create:
            owner_id = animal_data.pop("owner_id")
            animal_schema = schemas.AnimalCreate(**animal_data)
            animal = crud.create_animal(db, animal_schema, owner_id)
            created_animals.append(animal)
            owner_name = user1.name if owner_id == user1.id else user2.name
            print(f"   ✅ Created animal: {animal.icon_emoji} {animal.name} ({animal.species}) - Owner: {owner_name}")
        
        # ============= Create Test Chat Messages =============
        print("\n💬 Creating chat messages...")
        
        # Messages for Buddy (first animal)
        buddy = created_animals[0]
        messages = [
            {
                "animal_id": buddy.id,
                "sender": "Owner",
                "text": "My dog has been coughing lately. Should I be worried?",
                "severity": "moderate"
            },
            {
                "animal_id": buddy.id,
                "sender": "AI",
                "text": "Coughing in dogs can have various causes. If it's persistent, it could indicate kennel cough, allergies, or respiratory issues. Monitor for other symptoms like lethargy or loss of appetite. If it continues for more than a few days, consult your veterinarian.",
                "severity": "moderate",
                "medicine_suggestion": '{"recommendation": "Consult vet if persists", "possible_causes": ["Kennel cough", "Allergies", "Respiratory infection"]}'
            },
            {
                "animal_id": buddy.id,
                "sender": "Owner",
                "text": "He also seems less energetic than usual.",
                "severity": "moderate"
            },
            {
                "animal_id": buddy.id,
                "sender": "AI",
                "text": "Combined with the cough, decreased energy could indicate an infection. I recommend scheduling a vet appointment soon. In the meantime, ensure he stays hydrated and rests.",
                "severity": "urgent",
                "medicine_suggestion": '{"recommendation": "Schedule vet appointment", "urgency": "Soon", "care_tips": ["Keep hydrated", "Allow rest", "Monitor temperature"]}'
            }
        ]
        
        for msg_data in messages:
            msg_schema = schemas.ChatMessageCreate(**msg_data)
            msg = crud.create_chat_message(db, msg_schema)
            sender_icon = "👤" if msg.sender == "Owner" else "🤖"
            print(f"   ✅ {sender_icon} {msg.sender}: {msg.text[:50]}...")
        
        # Messages for Whiskers
        whiskers = created_animals[1]
        messages_whiskers = [
            {
                "animal_id": whiskers.id,
                "sender": "Owner",
                "text": "What's the best diet for a Persian cat?",
                "severity": "low"
            },
            {
                "animal_id": whiskers.id,
                "sender": "AI",
                "text": "Persian cats benefit from high-quality protein sources, moderate fat content, and controlled carbohydrates. Look for foods with real meat as the first ingredient. They may also need hairball control formula due to their long fur.",
                "severity": "low",
                "medicine_suggestion": '{"diet_tips": ["High-protein food", "Hairball control formula", "Wet food for hydration"], "feeding_frequency": "2-3 times daily"}'
            }
        ]
        
        for msg_data in messages_whiskers:
            msg_schema = schemas.ChatMessageCreate(**msg_data)
            msg = crud.create_chat_message(db, msg_schema)
            sender_icon = "👤" if msg.sender == "Owner" else "🤖"
            print(f"   ✅ {sender_icon} {msg.sender}: {msg.text[:50]}...")
        
        print("\n" + "="*60)
        print("✨ Test data created successfully!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   👤 Users created: 2")
        print(f"   🐾 Animals created: {len(created_animals)}")
        print(f"   💬 Chat messages created: {len(messages) + len(messages_whiskers)}")
        print("\n🔑 Test Credentials:")
        print(f"   Email: john@example.com")
        print(f"   Password: password123")
        print(f"\n   Email: jane@example.com")
        print(f"   Password: password123")
        print("\n🌐 Test the API at: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()
