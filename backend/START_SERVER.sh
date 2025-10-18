#!/bin/bash

echo "🔍 Checking for existing setup..."

if [ ! -d ~/hackaton/venv ]; then
    echo "📦 First time setup - Installing everything..."
    cd ~
    rm -rf hackaton
    mkdir hackaton
    cd hackaton
    echo "📋 Copying files..."
    cp -r /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/* .
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 Installing packages (this takes 2-3 minutes)..."
    pip install --quiet --upgrade pip
    pip install fastapi==0.104.1 uvicorn==0.24.0 sqlalchemy==2.0.23 pydantic==2.5.0 python-dotenv==1.0.0
    pip install google-generativeai bcrypt python-jose cryptography email-validator python-multipart
    echo "✅ Installation complete!"
else
    echo "✅ Setup already exists"
fi

cd ~/hackaton
source venv/bin/activate
echo "🚀 Starting AnimalAI Server with Google Gemini..."
echo "📍 Server will be at: http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0
