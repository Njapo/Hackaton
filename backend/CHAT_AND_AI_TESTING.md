# 💬 Chat & AI Testing Guide

## ✅ Good News: You Have OpenAI Configured!

Your `.env` file has an OpenAI API key configured, so **YES, you will get real AI responses from GPT-3.5-turbo**!

---

## 🧪 Testing Chat (Without AI)

These endpoints save messages to the database but don't call OpenAI:

### 1. **Create a Manual Chat Message**
**Endpoint:** `POST /api/chat`

This is like the owner sending a message about their pet.

```json
{
  "animal_id": 1,
  "sender": "Owner",
  "text": "Buddy has been limping on his left front paw for 2 days. Should I be worried?",
  "severity": "moderate"
}
```

**What happens:**
- ✅ Message saved to database
- ✅ Returns message with ID and timestamp
- ❌ No AI response (you're just recording a message)

---

### 2. **View Chat History**
**Endpoint:** `GET /api/chat/{animal_id}`

Example: `GET /api/chat/1` (for Buddy)

**What you'll see:**
```json
[
  {
    "id": 1,
    "animal_id": 1,
    "sender": "Owner",
    "text": "Buddy seems less energetic lately...",
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
    "medicine_suggestion": "{...}"
  }
]
```

**All messages for that animal, in chronological order!**

---

## 🤖 Testing AI (With OpenAI Response)

### 3. **AI Chat - Get Real AI Response**
**Endpoint:** `POST /api/ai/chat`

This is the **main feature** - sends your question to OpenAI and gets a response!

```json
{
  "animal_id": 1,
  "message": "My dog Buddy has been coughing a lot. He's 5 years old and weighs 25kg. What could be wrong?"
}
```

**What happens:**
1. ✅ Your message is saved as sender="Owner"
2. ✅ Request sent to OpenAI GPT-3.5-turbo with animal context
3. ✅ AI response received (takes 2-5 seconds)
4. ✅ AI response saved as sender="AI"
5. ✅ Returns the AI's answer

**Expected Response:**
```json
{
  "message": "Based on Buddy's symptoms, coughing in dogs can be caused by several factors... [AI provides detailed veterinary advice]",
  "severity": "low",
  "medicine_suggestion": null,
  "chat_message_id": 7
}
```

**⚠️ Important:**
- This will use **real OpenAI API credits**
- Takes 2-5 seconds to respond
- If API key is invalid, you'll get an error

---

## 🎯 Step-by-Step AI Test

### Step 1: Make sure you're authorized
- Already logged in as john@example.com
- Should see 🔒 lock icon

### Step 2: Test with Buddy (animal_id=1)
1. Go to `POST /api/ai/chat`
2. Click "Try it out"
3. Enter:
```json
{
  "animal_id": 1,
  "message": "Buddy has been drinking a lot of water lately. Is this normal for a 5-year-old Golden Retriever?"
}
```
4. Click "Execute"
5. **Wait 2-5 seconds** (OpenAI is processing)

### Step 3: Check the response
You should see:
```json
{
  "message": "[Long AI response about hydration, diabetes, kidney issues, etc.]",
  "severity": "low",
  "medicine_suggestion": null,
  "chat_message_id": 10
}
```

### Step 4: Verify it was saved
1. Go to `GET /api/chat/1`
2. Execute
3. You should see TWO new messages:
   - Your question (sender="Owner")
   - AI's answer (sender="AI")

---

## 🧠 What the AI Knows

When you send a message, the AI receives:

```json
{
  "animal_info": {
    "name": "Buddy",
    "species": "Dog",
    "breed": "Golden Retriever",
    "age": 5,
    "weight": 25.0
  },
  "user_message": "Your question here..."
}
```

The AI is prompted to act as a **veterinary assistant** and provide:
- Health assessments
- Possible diagnoses
- General care advice
- Warning signs to watch for

**⚠️ Disclaimer:** The AI provides general information, not professional veterinary diagnosis.

---

## 🔍 Check AI Configuration

### Verify OpenAI is working:

```bash
# Check your OpenAI key is loaded
cd /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend
wsl bash -c "grep OPENAI_API_KEY .env"
```

Should show:
```
OPENAI_API_KEY=sk-proj-XrKE...
```

### Test OpenAI connection manually:
```python
# Run in Python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Say hello!"}],
    max_tokens=50
)
print(response.choices[0].message.content)
```

---

## 🐛 Troubleshooting

### Error: "AI request failed"
**Possible causes:**
1. Invalid OpenAI API key
2. OpenAI API quota exceeded
3. Network issues
4. OpenAI service down

**Check:**
```bash
# Test if key is valid
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Error: "Animal not found"
- Make sure you're using an animal_id that belongs to you
- John has animals: 1 (Buddy), 2 (Whiskers)
- Jane has animals: 3 (Charlie), 4 (Tweety)

### Response takes too long
- Normal! OpenAI can take 2-10 seconds for complex responses
- Longer questions = longer responses = more time

---

## 📊 Test Scenarios

### Scenario 1: General Health Question
```json
{
  "animal_id": 1,
  "message": "What's the best diet for a Golden Retriever?"
}
```

### Scenario 2: Symptom Check
```json
{
  "animal_id": 2,
  "message": "My cat Whiskers has been sneezing and has watery eyes. Should I take her to the vet?"
}
```

### Scenario 3: Behavioral Question
```json
{
  "animal_id": 1,
  "message": "Buddy has been barking at night. How can I help him sleep better?"
}
```

### Scenario 4: Emergency Situation
```json
{
  "animal_id": 2,
  "message": "Whiskers ate a lily plant. What should I do immediately?"
}
```
*AI should recognize urgency and recommend immediate vet visit*

---

## 💾 Data Persistence Verification

After AI chat, check database:

```bash
cd /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend
sqlite3 animalai.db "SELECT id, animal_id, sender, substr(text, 1, 50), timestamp FROM chat_messages ORDER BY timestamp DESC LIMIT 5;"
```

You should see:
- Your messages with sender='Owner'
- AI responses with sender='AI'
- All timestamped
- All stored permanently

---

## 🎉 Quick Test Command

Want to test everything at once? Try this in API docs:

1. **POST /api/ai/chat** with:
```json
{
  "animal_id": 1,
  "message": "Give me 3 quick health tips for Buddy"
}
```

2. Then **GET /api/chat/1** to see the full history

You should see the AI response immediately in step 1, and both messages saved in step 2!

---

## 📝 Summary

| Endpoint | Purpose | AI Involved? | Saves to DB? |
|----------|---------|--------------|--------------|
| `POST /api/chat` | Manual message | ❌ No | ✅ Yes |
| `GET /api/chat/{id}` | View history | ❌ No | ❌ Read only |
| `POST /api/ai/chat` | Ask AI | ✅ **YES** | ✅ Yes (2 messages) |

**Ready to test?** Start with `POST /api/ai/chat` - that's where the magic happens! 🚀

The AI will respond in 2-5 seconds with veterinary advice based on your pet's information!
