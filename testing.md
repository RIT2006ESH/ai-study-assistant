# 🧪 Testing Guide - AI Study Assistant

This guide provides step-by-step instructions to test all implemented features.

## Prerequisites

- Backend and frontend running
- Sample PDF or DOCX file for testing

---

## 1️⃣ Authentication Testing

### Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123",
    "full_name": "Test User"
  }'
```

**Expected Response:**

```json
{
  "id": 1,
  "email": "testuser@example.com",
  "full_name": "Test User",
  "role": "student",
  "is_active": true,
  "is_verified": false
}
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123"
  }'
```

**Save the `access_token` for subsequent requests!**

### Get Current User

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 2️⃣ Document Management Testing

### Upload a Document

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/document.pdf" \
  -F "title=Test Document" \
  -F "subject=Computer Science"
```

**Expected Response:**

```json
{
  "id": 1,
  "title": "Test Document",
  "processing_status": "completed",
  "file_size": 524288,
  "text_length": 5432
}
```

### List Documents

```bash
curl -X GET http://localhost:8000/api/documents/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Document Details

```bash
curl -X GET http://localhost:8000/api/documents/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Extracted Text

```bash
curl -X GET http://localhost:8000/api/documents/1/text \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 3️⃣ Q&A System Testing

### Ask a Question (Without Document Context)

```bash
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?"
  }'
```

### Ask a Question (With Document Context)

```bash
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main concepts in this document?",
    "document_id": 1
  }'
```

**Expected Response:**

```json
{
  "message": "Based on the document, the main concepts include...",
  "session_id": "uuid-here",
  "conversation_id": 1,
  "context_used": true
}
```

### Continue Conversation

```bash
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you explain that in simpler terms?",
    "document_id": 1,
    "session_id": "session-id-from-previous-response"
  }'
```

### Get Conversation History

```bash
curl -X GET http://localhost:8000/api/chat/history/YOUR_SESSION_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get All Sessions

```bash
curl -X GET http://localhost:8000/api/chat/sessions \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Submit Feedback

```bash
curl -X POST http://localhost:8000/api/chat/feedback/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_positive": true,
    "comment": "Very helpful explanation!"
  }'
```

---

## 4️⃣ Summarization Testing

### Generate Brief Summary

```bash
curl -X POST http://localhost:8000/api/summarize/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "brief"
  }'
```

### Generate Detailed Summary

```bash
curl -X POST http://localhost:8000/api/summarize/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "detailed",
    "focus_areas": ["algorithms", "data structures"]
  }'
```

**Expected Response:**

```json
{
  "document_id": 1,
  "summary": "This document covers...",
  "level": "detailed",
  "word_count": 234,
  "original_length": 5432
}
```

### Extract Key Points

```bash
curl -X POST http://localhost:8000/api/summarize/1/key-points \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 5️⃣ Integration Testing Scenarios

### Complete User Journey

1. **Register & Login**
2. **Upload a study document**
3. **Wait for processing to complete**
4. **Generate a summary**
5. **Ask questions about the content**
6. **Continue the conversation**
7. **Submit feedback**

### Python Test Script

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Register
response = requests.post(f"{BASE_URL}/api/auth/register", json={
    "email": "integration@test.com",
    "password": "TestPass123",
    "full_name": "Integration Test"
})
print("✓ User registered")

# 2. Login
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "integration@test.com",
    "password": "TestPass123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✓ User logged in")

# 3. Upload document
with open("sample.pdf", "rb") as f:
    files = {"file": f}
    data = {"title": "Test Doc", "subject": "Testing"}
    response = requests.post(
        f"{BASE_URL}/api/documents/upload",
        headers=headers,
        files=files,
        data=data
    )
doc_id = response.json()["id"]
print(f"✓ Document uploaded (ID: {doc_id})")

# 4. Wait for processing
time.sleep(2)

# 5. Get document
response = requests.get(
    f"{BASE_URL}/api/documents/{doc_id}",
    headers=headers
)
assert response.json()["processing_status"] == "completed"
print("✓ Document processed")

# 6. Generate summary
response = requests.post(
    f"{BASE_URL}/api/summarize/{doc_id}",
    headers=headers,
    json={"level": "moderate"}
)
summary = response.json()["summary"]
print(f"✓ Summary generated: {summary[:100]}...")

# 7. Ask question
response = requests.post(
    f"{BASE_URL}/api/chat/ask",
    headers=headers,
    json={
        "message": "What is this document about?",
        "document_id": doc_id
    }
)
answer = response.json()["message"]
session_id = response.json()["session_id"]
print(f"✓ Question answered: {answer[:100]}...")

# 8. Continue conversation
response = requests.post(
    f"{BASE_URL}/api/chat/ask",
    headers=headers,
    json={
        "message": "Can you elaborate?",
        "document_id": doc_id,
        "session_id": session_id
    }
)
print("✓ Conversation continued")

# 9. Get conversation history
response = requests.get(
    f"{BASE_URL}/api/chat/history/{session_id}",
    headers=headers
)
history = response.json()
print(f"✓ Retrieved {len(history)} conversation messages")

print("\n🎉 All tests passed!")
```

---

## 6️⃣ Error Handling Tests

### Invalid Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "wrong@example.com",
    "password": "wrong"
  }'
```

**Expected:** 401 Unauthorized

### Upload Without Token

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@document.pdf"
```

**Expected:** 403 Forbidden

### Access Non-Existent Document

```bash
curl -X GET http://localhost:8000/api/documents/999 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected:** 404 Not Found

### Upload Unsupported File Type

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@image.exe"
```

**Expected:** 400 Bad Request

---

## 7️⃣ Performance Testing

### Load Test with Apache Bench

```bash
# Test login endpoint
ab -n 100 -c 10 -p login.json -T application/json \
  http://localhost:8000/api/auth/login
```

### Multiple Concurrent Uploads

```python
import concurrent.futures
import requests

def upload_document(i):
    with open("sample.pdf", "rb") as f:
        files = {"file": f}
        response = requests.post(
            "http://localhost:8000/api/documents/upload",
            headers={"Authorization": f"Bearer {token}"},
            files=files
        )
    return response.status_code

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(upload_document, range(10)))

print(f"Success rate: {results.count(201)}/10")
```

---

## 8️⃣ Database Verification

### Check User Creation

```sql
psql -U studyai_user -d studyai_db

SELECT id, email, full_name, created_at FROM users;
```

### Check Document Processing

```sql
SELECT id, title, processing_status, text_length
FROM documents
WHERE user_id = 1;
```

### Check Conversation History

```sql
SELECT session_id, role, message, created_at
FROM conversations
WHERE user_id = 1
ORDER BY created_at DESC
LIMIT 10;
```

---

## 9️⃣ API Documentation Tests

### Access Swagger UI

Visit: http://localhost:8000/api/docs

**Test:**

1. Click "Authorize" button
2. Enter Bearer token
3. Try endpoints directly from UI

### Access ReDoc

Visit: http://localhost:8000/api/redoc

---

## 🔟 Frontend Testing (When Implemented)

### Manual Browser Tests

1. Navigate to http://localhost:5173
2. Register new account
3. Login
4. Upload a document
5. Ask questions in chat interface
6. Generate summary
7. View analytics

### Browser Console Tests

```javascript
// Test API connectivity
fetch("http://localhost:8000/health")
  .then((r) => r.json())
  .then(console.log);
```

---

## ✅ Checklist

### Backend

- [ ] Server starts without errors
- [ ] Database tables created
- [ ] User registration works
- [ ] User login returns token
- [ ] Protected routes require authentication
- [ ] Document upload works
- [ ] PDF text extraction works
- [ ] DOCX text extraction works
- [ ] Q&A returns relevant answers
- [ ] Conversation history saved
- [ ] Summary generation works
- [ ] All endpoints return proper status codes
- [ ] Error handling works correctly

### Database

- [ ] Users table populated
- [ ] Documents table populated
- [ ] Conversations table populated
- [ ] Foreign keys working
- [ ] Timestamps auto-updating

### API

- [ ] All endpoints documented
- [ ] Swagger UI accessible
- [ ] Authentication working
- [ ] Rate limiting (if implemented)
- [ ] CORS configured correctly

---

## 🐛 Common Issues & Solutions

### Issue: "Module not found" errors

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Database connection fails

```bash
# Check PostgreSQL is running
pg_isready

# Verify credentials in .env
cat backend/.env | grep DATABASE_URL
```

### Issue: Document processing fails

```bash
# Check uploaded file
ls -lh backend/uploads/

# Check logs
tail -f backend.log
```

### Issue: AI responses fail

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Check .env file
cat backend/.env | grep API_KEY
```

---

## 📊 Test Results Template

```
Date: _________
Tester: _________

Authentication:          ✅ / ❌
Document Upload:         ✅ / ❌
Document Processing:     ✅ / ❌
Q&A System:             ✅ / ❌
Summarization:          ✅ / ❌
Error Handling:         ✅ / ❌

Notes:
_______________________
_______________________
```

---

## 🎯 Next Steps After Testing

1. ✅ Fix any identified bugs
2. ✅ Optimize slow endpoints
3. ✅ Add more test cases
4. ✅ Implement remaining features
5. ✅ Write unit tests
6. ✅ Setup CI/CD pipeline

---

**Happy Testing! 🧪**
