#!/usr/bin/env bash
# AutoCart Render Production Build Script (Root)
set -o errexit

echo "==> Upgrading pip..."
pip install --upgrade pip

echo "==> Installing backend dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
elif [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt
fi

echo "==> Collecting static files..."
if [ -f "manage.py" ]; then
    python manage.py collectstatic --no-input
elif [ -f "backend/manage.py" ]; then
    python backend/manage.py collectstatic --no-input
fi

echo "==> Running database migrations..."
if [ -f "manage.py" ]; then
    python manage.py migrate --no-input
elif [ -f "backend/manage.py" ]; then
    python backend/manage.py migrate --no-input
fi

echo "==> AutoCart backend build completed successfully!"
