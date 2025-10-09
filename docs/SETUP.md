# AI Study Assistant - Setup Guide

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Node.js 18+ (for frontend)
- Git

---

## Backend Setup

### 1. Clone and Navigate

```bash
# After creating the folder structure, navigate to backend
cd ai-study-assistant/backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Database Setup

```bash
# Start PostgreSQL (if not running)
# On Mac with Homebrew:
brew services start postgresql@14

# On Linux:
sudo systemctl start postgresql

# Create database
psql -U postgres
CREATE DATABASE studyai_db;
CREATE USER studyai_user WITH PASSWORD 'studyai_pass';
GRANT ALL PRIVILEGES ON DATABASE studyai_db TO studyai_user;
\q
```

### 5. Redis Setup

```bash
# Start Redis
# On Mac:
brew services start redis

# On Linux:
sudo systemctl start redis

# Verify Redis is running:
redis-cli ping
# Should return: PONG
```

### 6. Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env
```

**Minimum required variables:**

```env
DATABASE_URL=postgresql+asyncpg://studyai_user:studyai_pass@localhost:5432/studyai_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this
OPENAI_API_KEY=sk-your-openai-key
```

### 7. Initialize Database

```bash
# Run database migrations
alembic upgrade head

# Or if Alembic isn't configured yet, tables will be created on first run
```

### 8. Run Backend Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the main.py directly
python -m app.main
```

**Backend should now be running at:** `http://localhost:8000`

**API Documentation:** `http://localhost:8000/api/docs`

---

## Frontend Setup

### 1. Navigate to Frontend

```bash
cd ../frontend
```

### 2. Initialize NPM Project

```bash
npm init -y
```

### 3. Install Dependencies

```bash
# Core dependencies
npm install react react-dom react-router-dom axios

# Dev dependencies
npm install -D vite @vitejs/plugin-react tailwindcss postcss autoprefixer

# UI libraries
npm install lucide-react recharts

# State management
npm install @tanstack/react-query zustand
```

### 4. Initialize Tailwind

```bash
npx tailwindcss init -p
```

### 5. Environment Variables

```bash
# Create .env file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
```

### 6. Run Frontend

```bash
npm run dev
```

**Frontend should now be running at:** `http://localhost:5173`

---

## Testing the Setup

### 1. Test Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### 2. Test User Registration

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234",
    "full_name": "Test User"
  }'
```

### 3. Test Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234"
  }'
```

---

## Docker Setup (Alternative)

### 1. Create docker-compose.yml

```yaml
version: "3.8"

services:
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: studyai_db
      POSTGRES_USER: studyai_user
      POSTGRES_PASSWORD: studyai_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://studyai_user:studyai_pass@db:5432/studyai_db
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app

volumes:
  postgres_data:
```

### 2. Run with Docker

```bash
docker-compose up -d
```

---

## Common Issues & Solutions

### Issue: Database connection failed

**Solution:**

```bash
# Check if PostgreSQL is running
pg_isready

# Check connection string in .env
# Ensure user and database exist
psql -U postgres -l
```

### Issue: Redis connection failed

**Solution:**

```bash
# Check if Redis is running
redis-cli ping

# Start Redis if not running
redis-server
```

### Issue: Module not found errors

**Solution:**

```bash
# Ensure virtual environment is activated
which python  # Should point to venv

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Port already in use

**Solution:**

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

---

## Development Workflow

### 1. Start All Services

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Redis (if not running as service)
redis-server

# Terminal 4: PostgreSQL (if not running as service)
postgres -D /usr/local/var/postgres
```

### 2. Database Migrations (Alembic)

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

### 3. Running Tests

```bash
# Backend tests
pytest tests/

# With coverage
pytest --cov=app tests/
```

---

## Next Steps

After setup is complete:

1. ✅ Test authentication endpoints
2. ✅ Implement document upload functionality
3. ✅ Add PDF processing service
4. ✅ Integrate OpenAI API
5. ✅ Build frontend components
6. ✅ Add vector database (Pinecone/Chroma)

---

## Getting Help

- **Backend API Docs**: http://localhost:8000/api/docs
- **Check Logs**: `tail -f logs/app.log`
- **Database Console**: `psql -U studyai_user -d studyai_db`

Happy coding!
