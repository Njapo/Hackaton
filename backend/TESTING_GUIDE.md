# Testing Guide for AnimalAI Backend

## 📍 Database Location

Your SQLite database is located at:
```
C:\Users\v-nikolozij\Desktop\Hackaton\backend\animalai.db
```

The database is automatically created when the server starts. It's a single file that contains all your data.

## 🧪 How to Test the API

### Step 1: Populate Database with Test Data

Run the test data script to add sample users, animals, and chat messages:

```bash
# Make sure you're in the backend directory
cd C:\Users\v-nikolozij\Desktop\Hackaton\backend

# Activate virtual environment (if not already active)
wsl bash -c 'cd /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend && source venv/bin/activate && python test_data.py'
```

This creates:
- **2 test users** (John and Jane)
- **4 test animals** (2 dogs, 1 cat, 1 bird)
- **6 chat messages** (conversation examples)

### Step 2: Test via Interactive API Docs

1. **Open your browser** and go to: http://localhost:8000/docs

2. **Test Authentication:**
   - Click on `POST /api/auth/login`
   - Click "Try it out"
   - Enter credentials:
     ```json
     {
       "email": "john@example.com",
       "password": "password123"
     }
     ```
   - Click "Execute"
   - **Copy the `access_token`** from the response

3. **Authorize Requests:**
   - Click the **🔓 Authorize** button at the top
   - Paste the token in the format: `Bearer YOUR_TOKEN_HERE`
   - Click "Authorize"

4. **Test Endpoints:**
   
   **Get Your Animals:**
   - Click `GET /api/animals/my`
   - Click "Try it out" → "Execute"
   - You should see Buddy (dog) and Whiskers (cat)
   
   **Get Chat History:**
   - Click `GET /api/chat/{animal_id}`
   - Enter animal_id: `1` (Buddy's ID)
   - Click "Execute"
   - You'll see the conversation about Buddy's cough
   
   **Create New Animal:**
   - Click `POST /api/animals`
   - Try adding your own pet!
   ```json
   {
     "name": "Max",
     "species": "Dog",
     "breed": "Labrador",
     "age": 4,
     "weight": 35.0,
     "icon_emoji": "🐕"
   }
   ```

### Step 3: Test with Curl (Alternative)

```bash
# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"password123"}'

# Get animals (replace TOKEN with your actual token)
curl -X GET "http://localhost:8000/api/animals/my" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📊 Database Contents After Test Data

### Users Table
| ID | Email | Name |
|----|-------|------|
| 1 | john@example.com | John Doe |
| 2 | jane@example.com | Jane Smith |

### Animals Table
| ID | Owner | Name | Species | Emoji |
|----|-------|------|---------|-------|
| 1 | John | Buddy | Dog | 🐕 |
| 2 | John | Whiskers | Cat | 🐱 |
| 3 | Jane | Charlie | Dog | 🐶 |
| 4 | Jane | Tweety | Bird | 🐦 |

### Chat Messages Table
- **6 messages** total
- Conversation about Buddy's health (coughing)
- Conversation about Whiskers' diet

## 🔍 Viewing the Database Directly

### Option 1: Using SQLite Browser (Recommended)

1. Download **DB Browser for SQLite**: https://sqlitebrowser.org/
2. Open the file: `C:\Users\v-nikolozij\Desktop\Hackaton\backend\animalai.db`
3. Browse tables: users, animals, chat_messages

### Option 2: Using WSL Command Line

```bash
wsl bash -c 'cd /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend && sqlite3 animalai.db "SELECT * FROM users;"'

wsl bash -c 'cd /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend && sqlite3 animalai.db "SELECT * FROM animals;"'

wsl bash -c 'cd /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend && sqlite3 animalai.db "SELECT * FROM chat_messages;"'
```

## 🧹 Reset Database

To start fresh:

```bash
# Stop the server (Ctrl+C)
# Delete the database
wsl bash -c 'cd /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend && rm animalai.db'
# Restart the server (it will recreate the database)
wsl bash /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/start.sh
# Run test_data.py again
```

## 🎯 Quick Test Checklist

- [ ] Server is running (http://localhost:8000)
- [ ] Test data is loaded (`python test_data.py`)
- [ ] Can login with john@example.com
- [ ] Can see animals at `/api/animals/my`
- [ ] Can view chat messages at `/api/chat/1`
- [ ] Can create new animal
- [ ] Can send message to AI

## 💡 Testing AI Chat

Try the AI chat endpoint:

1. Go to `POST /api/ai/chat`
2. Use this request:
```json
{
  "animal_id": 1,
  "message": "What should I feed my Golden Retriever?"
}
```

The AI will respond and save both your message and its response to the chat history!

## 🐛 Troubleshooting

**Database not found?**
- Make sure the server has been started at least once
- Check: `C:\Users\v-nikolozij\Desktop\Hackaton\backend\animalai.db`

**Can't see test data?**
- Run `python test_data.py` to populate the database

**Authentication fails?**
- Make sure you copied the full token
- Token format should be: `Bearer YOUR_TOKEN_HERE`
- Tokens expire after 30 minutes (default)

**404 errors?**
- Check that the server is running
- Visit http://localhost:8000/docs to see all available endpoints
