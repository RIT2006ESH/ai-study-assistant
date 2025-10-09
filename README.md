# 🎓 AI-Powered Study Assistant

An intelligent, personalized study companion that helps students learn more effectively through AI-powered document summarization, Q&A, problem-solving, and adaptive learning.

## ✨ Features

### ✅ Implemented (MVP)

- 🔐 **User Authentication** - Secure registration and login with JWT
- 📄 **Document Upload** - Support for PDF, DOCX, TXT files
- 📝 **Text Extraction** - Automatic content extraction from documents
- 💬 **Q&A System** - Ask questions about your study materials
- 📋 **Summarization** - Generate summaries at different detail levels
- 🔍 **Semantic Search** - Intelligent context retrieval for accurate answers
- 📊 **Document Management** - Organize and track your study materials

### 🚧 Coming Soon (Phase 2)

- 🧮 **Problem Solver** - Step-by-step solutions for Math, Physics, CS
- 🎴 **Flashcard Generator** - Auto-generate flashcards from documents
- 📈 **Progress Tracking** - Analytics and learning insights
- 🗓️ **Study Planner** - Personalized study schedules
- 🎯 **Adaptive Learning** - AI adjusts to your learning style
- 🖼️ **Image/Audio Support** - OCR and transcription

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Node.js 18+

# Optional (for AI features)
- OpenAI API Key OR Anthropic API Key
```

### Option 1: Automated Setup (Recommended)

```bash
# 1. Create project structure
./setup.sh

# 2. Start services (PostgreSQL & Redis must be running)
chmod +x run.sh
./run.sh

# The script will:
# - Check if services are running
# - Create database
# - Install dependencies
# - Start backend and frontend
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add your API keys

# Create database
psql -U postgres
CREATE DATABASE studyai_db;
CREATE USER studyai_user WITH PASSWORD 'studyai_pass';
GRANT ALL PRIVILEGES ON DATABASE studyai_db TO studyai_user;
\q

# Run backend
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Run frontend
npm run dev
```

---

## 📚 API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Key Endpoints

#### Authentication

```bash
POST /api/auth/register  # Register new user
POST /api/auth/login     # Login
GET  /api/auth/me        # Get current user
POST /api/auth/refresh   # Refresh token
```

#### Documents

```bash
POST /api/documents/upload     # Upload document
GET  /api/documents/           # List documents
GET  /api/documents/{id}       # Get document
DELETE /api/documents/{id}     # Delete document
GET  /api/documents/{id}/text  # Get extracted text
```

#### Chat & Q&A

```bash
POST /api/chat/ask                # Ask question
GET  /api/chat/history/{session}  # Get chat history
GET  /api/chat/sessions           # List sessions
POST /api/chat/feedback/{id}      # Submit feedback
```

#### Summarization

```bash
POST /api/summarize/{document_id}        # Generate summary
POST /api/summarize/{document_id}/key-points  # Extract key points
```

---

## 🧪 Testing the API

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123",
    "full_name": "John Student"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123"
  }'
```

Save the `access_token` from the response.

### 3. Upload a Document

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/document.pdf" \
  -F "title=My Study Notes" \
  -F "subject=Mathematics"
```

### 4. Ask a Question

```bash
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main concepts in this document?",
    "document_id": 1
  }'
```

---

## 🗂️ Project Structure

```
ai-study-assistant/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # API endpoints
│   │   ├── core/                # Security, database
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   │   ├── ai_engine/       # LLM integration
│   │   │   ├── document_processing/  # File processing
│   │   │   ├── qa_system/       # Q&A logic
│   │   │   └── summarization/   # Summarization
│   │   ├── utils/               # Utilities
│   │   └── main.py              # FastAPI app
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API calls
│   │   └── App.jsx
│   ├── package.json
│   └── .env
├── docker-compose.yml
├── run.sh
└── README.md
```

---

## 🔧 Configuration

### Environment Variables

**Backend (.env)**

```env
# Database
DATABASE_URL=postgresql+asyncpg://studyai_user:studyai_pass@localhost:5432/studyai_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# AI APIs (Choose one or both)
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# AI Models
AI_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small
```

**Frontend (.env)**

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🐳 Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🛠️ Development

### Running Tests

```bash
cd backend
pytest tests/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Adding New Features

1. **Create Model** in `models/`
2. **Create Schema** in `schemas/`
3. **Create Service** in `services/`
4. **Create Route** in `api/routes/`
5. **Register Route** in `main.py`

---

## 📖 Usage Examples

### Python Client Example

```python
import requests

API_URL = "http://localhost:8000"

# Login
response = requests.post(f"{API_URL}/api/auth/login", json={
    "email": "student@example.com",
    "password": "SecurePass123"
})
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Upload document
files = {"file": open("textbook.pdf", "rb")}
response = requests.post(
    f"{API_URL}/api/documents/upload",
    headers=headers,
    files=files,
    data={"title": "Chapter 5 - Calculus"}
)
doc_id = response.json()["id"]

# Ask question
response = requests.post(
    f"{API_URL}/api/chat/ask",
    headers=headers,
    json={
        "message": "Explain the concept of derivatives",
        "document_id": doc_id
    }
)
answer = response.json()["message"]
print(answer)
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 🆘 Troubleshooting

### Backend won't start

```bash
# Check if PostgreSQL is running
pg_isready

# Check if Redis is running
redis-cli ping

# View backend logs
tail -f backend.log
```

### Database connection errors

```bash
# Reset database
dropdb studyai_db
createdb studyai_db
```

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

---

## 📧 Support

For issues and questions:

- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/api/docs`

---

## 🎯 Roadmap

- [x] User authentication
- [x] Document upload & processing
- [x] Q&A system
- [x] Summarization
- [ ] Problem solver
- [ ] Flashcard generation
- [ ] Progress analytics
- [ ] Mobile app
- [ ] Collaborative features
- [ ] Integration with LMS platforms

---

**Built with ❤️ for students worldwide**
