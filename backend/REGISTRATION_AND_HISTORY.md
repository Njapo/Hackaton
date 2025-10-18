# Registration & Data Persistence Guide

## ✅ Yes, You Can Register!

Your backend has **full registration logic** implemented and working. Here's what it does:

### Registration Endpoint: `POST /api/auth/register`

**What it does:**
1. ✅ Checks if email already exists
2. ✅ Hashes password securely with bcrypt
3. ✅ Creates new user in database
4. ✅ Returns user data (without password)

**Test Registration:**
```bash
# Go to http://localhost:8000/docs
# Find "POST /api/auth/register" endpoint
# Click "Try it out"
# Use this JSON:
{
  "email": "newuser@example.com",
  "name": "New User",
  "password": "securePassword123"
}
```

---

## 💾 Data Persistence - YES, All History is Kept!

Your database **keeps ALL conversation history** permanently in SQLite. Here's how:

### Database Location
- **File:** `backend/animalai.db` (SQLite database)
- **Persistent:** Data survives server restarts
- **Size:** Currently 32KB with test data

### What's Stored:

#### 1. **Users Table** 🔐
```
- id (unique identifier)
- email (login credential)
- password_hash (secure bcrypt hash)
- name (display name)
- created_at (registration timestamp)
```

#### 2. **Animals Table** 🐾
```
- id (unique identifier)
- owner_id (links to User)
- name (e.g., "Buddy")
- species (e.g., "Dog")
- breed (e.g., "Golden Retriever")
- age (in years)
- weight (in kg)
- icon_emoji (e.g., "🐕")
```

#### 3. **ChatMessages Table** 💬 (FULL HISTORY!)
```
- id (unique identifier)
- animal_id (links to Animal)
- sender ('Owner' or 'AI')
- text (message content)
- severity ('low', 'moderate', 'urgent')
- timestamp (when message was sent)
- medicine_suggestion (JSON with AI recommendations)
```

---

## 🔍 How History Works

### Every conversation is preserved:
1. **User asks about their pet** → Stored as ChatMessage with sender='Owner'
2. **AI responds with advice** → Stored as ChatMessage with sender='AI'
3. **All timestamps recorded** → Messages ordered chronologically
4. **Severity tracked** → 'low', 'moderate', or 'urgent'
5. **Medicine suggestions saved** → JSON format with dosage, warnings, etc.

### Retrieving History:
```bash
# Get all messages for an animal (e.g., animal_id=1)
GET /api/chat/1

# Returns ALL messages in order:
[
  {
    "id": 1,
    "animal_id": 1,
    "sender": "Owner",
    "text": "Buddy seems less energetic...",
    "severity": "moderate",
    "timestamp": "2024-10-18T10:30:00",
    "medicine_suggestion": null
  },
  {
    "id": 2,
    "animal_id": 1,
    "sender": "AI",
    "text": "I understand Buddy is less energetic...",
    "severity": "moderate",
    "timestamp": "2024-10-18T10:30:15",
    "medicine_suggestion": "{\"suggested_medicines\": [...], \"dosage\": \"...\", ...}"
  }
  // ... all other messages
]
```

---

## 🧪 Test Registration & History

### Step 1: Register New User
```bash
1. Open http://localhost:8000/docs
2. Find "POST /api/auth/register"
3. Click "Try it out"
4. Enter:
   {
     "email": "testuser@example.com",
     "name": "Test User",
     "password": "mypassword123"
   }
5. Click "Execute"
6. Should get 200 response with user data
```

### Step 2: Login with New Account
```bash
1. Find "POST /api/auth/login"
2. Enter:
   {
     "email": "testuser@example.com",
     "password": "mypassword123"
   }
3. Copy the "access_token" from response
4. Click "Authorize" button at top
5. Enter: Bearer <your_token>
```

### Step 3: Create Animal
```bash
1. Find "POST /api/animals"
2. Enter:
   {
     "name": "Max",
     "species": "Dog",
     "breed": "Labrador",
     "age": 3,
     "weight": 30.5,
     "icon_emoji": "🐕"
   }
3. Note the animal "id" in response (e.g., 5)
```

### Step 4: Start Conversation
```bash
1. Find "POST /api/chat"
2. Enter:
   {
     "animal_id": 5,
     "sender": "Owner",
     "text": "Max has been coughing a lot lately",
     "severity": "moderate"
   }
3. Message is saved to database!
```

### Step 5: Get AI Response
```bash
1. Find "POST /api/ai/chat"
2. Enter:
   {
     "animal_id": 5,
     "message": "Max has been coughing. Should I be worried?"
   }
3. AI response is ALSO saved to database automatically
```

### Step 6: View Full History
```bash
1. Find "GET /api/chat/{animal_id}"
2. Enter animal_id: 5
3. See ALL messages for Max, in order
4. Includes your messages AND AI responses
```

---

## 🔒 Data Security & Privacy

### What's Protected:
- ✅ Passwords are **never** stored in plain text (bcrypt hashed)
- ✅ Each user can only access **their own** animals
- ✅ Chat history is **private** to animal owner
- ✅ JWT tokens expire after 30 minutes
- ✅ All endpoints require authentication (except register/login)

### Relationship Enforcement:
```
User → Animals → ChatMessages
  └─ One user has many animals
      └─ One animal has many messages
```

When you delete an animal, all its chat messages are automatically deleted (CASCADE).

---

## 📊 Current Test Data

Your database already has sample data:

### Users:
- john@example.com (password: password123)
- jane@example.com (password: password123)

### Animals:
- Buddy 🐕 (John's dog) - Has 3 messages
- Whiskers 🐱 (John's cat) - Has 3 messages
- Charlie 🐶 (Jane's dog) - No messages yet
- Tweety 🐦 (Jane's bird) - No messages yet

### Chat History Example (Buddy):
```
1. Owner: "Buddy seems less energetic lately..."
2. AI: "I understand Buddy is less energetic..." (with medicine suggestions)
3. Owner: "Thanks! Should I change his diet?"
```

---

## 🚀 Quick Test Script

Run this to verify everything works:

```bash
# 1. Check database size (should grow as you add data)
cd /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend
ls -lh animalai.db

# 2. View all tables
sqlite3 animalai.db ".tables"

# 3. Count records
sqlite3 animalai.db "SELECT COUNT(*) FROM users;"
sqlite3 animalai.db "SELECT COUNT(*) FROM animals;"
sqlite3 animalai.db "SELECT COUNT(*) FROM chat_messages;"

# 4. See all chat messages with details
sqlite3 animalai.db "SELECT id, animal_id, sender, substr(text, 1, 50) as message, timestamp FROM chat_messages ORDER BY timestamp;"
```

---

## ✨ Summary

**Registration:** ✅ Fully working - register unlimited users
**History:** ✅ 100% persistent - ALL conversations stored forever
**Privacy:** ✅ Secure - users only see their own data
**Scalability:** ✅ SQLite can handle thousands of messages

**Your backend has enterprise-grade data persistence!** 🎉

Every message, every animal, every user interaction is safely stored in the database and will remain there unless explicitly deleted.
