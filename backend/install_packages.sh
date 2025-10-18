#!/bin/bash

# Simple install script to avoid WSL filesystem issues

cd "$(dirname "$0")"

echo "Installing packages one by one to avoid filesystem issues..."

./venv/bin/pip install --upgrade pip
./venv/bin/pip install fastapi==0.104.1
./venv/bin/pip install uvicorn==0.24.0  
./venv/bin/pip install sqlalchemy==2.0.23
./venv/bin/pip install bcrypt==5.0.0
./venv/bin/pip install python-jose==3.3.0
./venv/bin/pip install cryptography
./venv/bin/pip install email-validator==2.3.0

echo "✅ Installation complete!"
echo "Now run: ./venv/bin/uvicorn app.main:app --reload"
