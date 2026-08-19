#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Ensure ML data directories exist..."
mkdir -p ml/data/raw
mkdir -p ml/data/processed/features
mkdir -p ml/data/processed/models
