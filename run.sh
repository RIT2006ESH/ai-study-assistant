#!/bin/bash

# AI Study Assistant - Quick Start Script
# This script sets up and runs the application

set -e  # Exit on error

echo "🚀 AI Study Assistant - Quick Start"
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if required services are running
check_postgres() {
    if pg_isready -q; then
        print_success "PostgreSQL is running"
        return 0
    else
        print_error "PostgreSQL is not running"
        echo "Please start PostgreSQL:"
        echo "  Mac: brew services start postgresql@14"
        echo "  Linux: sudo systemctl start postgresql"
        return 1
    fi
}

check_redis() {
    if redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is running"
        return 0
    else
        print_error "Redis is not running"
        echo "Please start Redis:"
        echo "  Mac: brew services start redis"
        echo "  Linux: sudo systemctl start redis"
        return 1
    fi
}

# Setup database
setup_database() {
    echo ""
    echo "Setting up database..."
    
    if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw studyai_db; then
        print_warning "Database 'studyai_db' already exists"
    else
        psql -U postgres <<EOF
CREATE DATABASE studyai_db;
CREATE USER studyai_user WITH PASSWORD 'studyai_pass';
GRANT ALL PRIVILEGES ON DATABASE studyai_db TO studyai_user;
EOF
        print_success "Database created"
    fi
}

# Setup backend
setup_backend() {
    echo ""
    echo "Setting up backend..."
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing Python dependencies..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    print_success "Dependencies installed"
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Copying from .env.example"
        cp .env.example .env
        echo ""
        print_error "⚠️  IMPORTANT: Edit backend/.env and add your API keys!"
        echo "Required: OPENAI_API_KEY or ANTHROPIC_API_KEY"
        read -p "Press Enter after updating .env file..."
    fi
    
    cd ..
}

# Setup frontend
setup_frontend() {
    echo ""
    echo "Setting up frontend..."
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "Installing Node dependencies..."
        npm install
        print_success "Frontend dependencies installed"
    else
        print_success "Frontend dependencies already installed"
    fi
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        echo "VITE_API_BASE_URL=http://localhost:8000" > .env
        print_success "Frontend .env created"
    fi
    
    cd ..
}

# Run the application
run_app() {
    echo ""
    echo "Starting AI Study Assistant..."
    echo ""
    
    # Start backend in background
    cd backend
    source venv/bin/activate
    echo "Starting backend server on http://localhost:8000"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    sleep 3
    
    # Check if backend started successfully
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend running at http://localhost:8000"
        print_success "API Documentation: http://localhost:8000/api/docs"
    else
        print_error "Backend failed to start. Check backend.log for errors"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    # Start frontend in background
    cd frontend
    echo "Starting frontend server on http://localhost:5173"
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    sleep 3
    print_success "Frontend running at http://localhost:5173"
    
    echo ""
    echo "=========================================="
    echo "✅ AI Study Assistant is now running!"
    echo "=========================================="
    echo ""
    echo "Access the application:"
    echo "  • Frontend: http://localhost:5173"
    echo "  • Backend API: http://localhost:8000"
    echo "  • API Docs: http://localhost:8000/api/docs"
    echo ""
    echo "Logs:"
    echo "  • Backend: tail -f backend.log"
    echo "  • Frontend: tail -f frontend.log"
    echo ""
    echo "To stop the servers:"
    echo "  • Press Ctrl+C in this terminal"
    echo "  • Or run: ./stop.sh"
    echo ""
    
    # Save PIDs for stopping later
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
    
    # Wait for user interrupt
    trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend.pid .frontend.pid; print_success 'Servers stopped'; exit 0" INT
    
    # Keep script running
    wait
}

# Main execution
main() {
    # Check services
    check_postgres || exit 1
    check_redis || exit 1
    
    # Setup database
    setup_database
    
    # Setup backend and frontend
    setup_backend
    setup_frontend
    
    # Run the application
    run_app
}

# Run main function
main