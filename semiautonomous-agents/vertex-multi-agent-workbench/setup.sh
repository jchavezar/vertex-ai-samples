#!/bin/bash
# Vertex Cowork Setup Script

set -e

echo "Setting up Vertex Cowork..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check Node version
node_version=$(node --version 2>&1)
echo "Node version: $node_version"

# Backend setup
echo ""
echo "Setting up backend..."
cd backend

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt

echo "Backend dependencies installed."

# Frontend setup
echo ""
echo "Setting up frontend..."
cd ../frontend

npm install --silent

echo "Frontend dependencies installed."

# Create .env if not exists
cd ..
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "Created .env file. Please update with your GCP project ID."
fi

echo ""
echo "Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Update .env with your GCP project ID"
echo "  2. Backend: cd backend && source .venv/bin/activate && python main.py"
echo "  3. Frontend: cd frontend && npm run dev (in another terminal)"
echo ""
echo "Access:"
echo "  - Frontend UI:  http://localhost:3000"
echo "  - Backend API:  http://localhost:8080"
echo "  - API Docs:     http://localhost:8080/docs"
echo ""
echo "Or use Docker: docker-compose up -d"
