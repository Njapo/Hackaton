# AnimalAI Database Schema Documentation

This document describes the complete database schema for the AnimalAI backend.

## Database Models

### 1. User Model

**Table Name:** `users`

**Purpose:** Stores user authentication and profile information

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| id | Integer | PK, Auto-increment | Unique user identifier |
| email | String(100) | Unique, Not Null, Indexed | User's email address for login |
| password_hash | String(255) | Not Null | Bcrypt hashed password |
| name | String(100) | Not Null | User's full name |
| created_at | DateTime | Default: now() | Account creation timestamp |

**Relationships:**
- One-to-Many with `Animal` (user can own multiple animals)

**CRUD Operations:**
- `create_user(db, user)` - Register new user
- `get_user(db, user_id)` - Get user by ID
- `get_user_by_email(db, email)` - Get user by email
- `get_users(db, skip, limit)` - List all users (paginated)
- `update_user(db, user_id, user_update)` - Update user info
- `delete_user(db, user_id)` - Delete user account

---

### 2. Animal Model

**Table Name:** `animals`

**Purpose:** Stores information about pets/animals owned by users

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| id | Integer | PK, Auto-increment | Unique animal identifier |
| owner_id | Integer | FK(users.id), Not Null | Reference to owning user |
| name | String(100) | Not Null | Animal's name |
| species | String(50) | Not Null | Type of animal (Dog, Cat, etc.) |
| breed | String(100) | Nullable | Specific breed |
| age | Integer | Nullable | Age in years |
| weight | Float | Nullable | Weight in kilograms |
| icon_emoji | String(10) | Default: "🐾" | Emoji icon for the animal |

**Relationships:**
- Many-to-One with `User` (each animal belongs to one user)
- One-to-Many with `ChatMessage` (animal can have multiple chat messages)

**CRUD Operations:**
- `create_animal(db, animal, owner_id)` - Add new animal
- `get_animal(db, animal_id)` - Get animal by ID
- `get_animals(db, skip, limit)` - List all animals (paginated)
- `get_animals_by_owner(db, owner_id, skip, limit)` - Get user's animals
- `get_animals_by_species(db, species, skip, limit)` - Filter by species
- `update_animal(db, animal_id, animal_update)` - Update animal info
- `delete_animal(db, animal_id)` - Delete animal

---

### 3. ChatMessage Model

**Table Name:** `chat_messages`

**Purpose:** Stores conversation history between owner and AI for each animal

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| id | Integer | PK, Auto-increment | Unique message identifier |
| animal_id | Integer | FK(animals.id), Not Null | Reference to animal |
| sender | String(10) | Not Null | 'Owner' or 'AI' |
| text | Text | Not Null | Message content |
| severity | String(20) | Default: 'low' | Health severity: 'low', 'moderate', 'urgent' |
| timestamp | DateTime | Default: now() | When message was sent |
| medicine_suggestion | Text | Nullable | Medicine recommendations (JSON or text) |

**Relationships:**
- Many-to-One with `Animal` (each message belongs to one animal)

**CRUD Operations:**
- `create_chat_message(db, message)` - Save new message
- `get_chat_message(db, message_id)` - Get message by ID
- `get_chat_messages_by_animal(db, animal_id, skip, limit)` - Get chat history
- `get_chat_messages_by_sender(db, animal_id, sender, skip, limit)` - Filter by sender
- `get_chat_messages_by_severity(db, animal_id, severity, skip, limit)` - Filter by severity
- `update_chat_message(db, message_id, message_update)` - Update message
- `delete_chat_message(db, message_id)` - Delete message
- `delete_all_chat_messages_for_animal(db, animal_id)` - Clear chat history

---

## Pydantic Schemas

### User Schemas
- `UserBase` - Base fields (email, name)
- `UserCreate` - For registration (includes password)
- `UserUpdate` - For updating profile (all fields optional)
- `UserInDB` / `User` - For responses (includes id, created_at)

### Animal Schemas
- `AnimalBase` - Base fields (name, species, breed, age, weight, icon_emoji)
- `AnimalCreate` - For creating animals
- `AnimalUpdate` - For updating animals (all fields optional)
- `AnimalInDB` / `Animal` - For responses (includes id, owner_id)
- `AnimalWithMessages` - Includes nested chat_messages list

### ChatMessage Schemas
- `ChatMessageBase` - Base fields (sender, text, severity, medicine_suggestion)
- `ChatMessageCreate` - For creating messages (includes animal_id)
- `ChatMessageUpdate` - For updating messages (all fields optional)
- `ChatMessageInDB` / `ChatMessage` - For responses (includes id, timestamp)

### Additional Schemas
- `Token` - JWT token response
- `TokenData` - Token payload
- `LoginRequest` - Login credentials
- `AIChatRequest` - AI chat request
- `AIChatResponse` - AI chat response with severity and suggestions

---

## Database Relationships Diagram

```
┌─────────────┐
│    User     │
│  (users)    │
└──────┬──────┘
       │ 1
       │ owns
       │ N
┌──────▼──────┐
│   Animal    │
│  (animals)  │
└──────┬──────┘
       │ 1
       │ has
       │ N
┌──────▼──────────┐
│  ChatMessage    │
│ (chat_messages) │
└─────────────────┘
```

---

## Usage Examples

### Creating a User
```python
from app import crud, schemas
from app.database import SessionLocal

db = SessionLocal()
user_data = schemas.UserCreate(
    email="john@example.com",
    name="John Doe",
    password="SecurePass123!"
)
user = crud.create_user(db, user_data)
db.close()
```

### Adding an Animal
```python
animal_data = schemas.AnimalCreate(
    name="Buddy",
    species="Dog",
    breed="Golden Retriever",
    age=3,
    weight=30.5,
    icon_emoji="🐕"
)
animal = crud.create_animal(db, animal_data, owner_id=user.id)
```

### Saving a Chat Message
```python
message_data = schemas.ChatMessageCreate(
    animal_id=animal.id,
    sender="Owner",
    text="My dog has been coughing lately",
    severity="moderate"
)
message = crud.create_chat_message(db, message_data)
```

---

## Database Migrations

After modifying models, recreate the database:

```bash
# Stop the server
# Delete the database file
rm animalai.db

# Restart the server (it will recreate tables automatically)
wsl bash /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/start.sh
```

Or use the init_db() function:
```python
from app.database import init_db
init_db()
```

---

## Notes

- All passwords are hashed using bcrypt before storing
- Email addresses are unique and indexed for fast lookups
- Timestamps use timezone-aware datetime
- Foreign keys use CASCADE delete (deleting a user deletes their animals and messages)
- Chat messages are ordered by timestamp descending (newest first)
- Medicine suggestions can be stored as JSON strings or plain text
