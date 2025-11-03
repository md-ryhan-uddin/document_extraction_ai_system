#!/bin/bash

echo "========================================"
echo "Document AI System - Setup Script"
echo "========================================"
echo ""

echo "Step 1: Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

echo "Step 2: Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

echo "Step 3: Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

echo "Step 4: Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ .env file created from .env.example"
    echo "⚠ IMPORTANT: Edit .env and add your API_KEY"
else
    echo "ℹ .env file already exists"
fi
echo ""

echo "Step 5: Running migrations..."
python manage.py makemigrations
python manage.py migrate
echo "✓ Database migrations completed"
echo ""

echo "Step 6: Creating directories..."
mkdir -p media staticfiles
echo "✓ Directories created"
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your AI API key"
echo "2. Create a superuser: python manage.py createsuperuser"
echo "3. Run the server: python manage.py runserver"
echo "4. Open http://127.0.0.1:8000/ in your browser"
echo ""
