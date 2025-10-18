#!/bin/bash
# AnimalAI Backend Startup Script

cd /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend
source venv/bin/activate

echo "=========================================="
echo "🐾 Starting AnimalAI Backend Server"
echo "=========================================="
echo ""
echo "📡 API Server: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "📖 ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

uvicorn app.main:app --reload --host 0.0.0.0
