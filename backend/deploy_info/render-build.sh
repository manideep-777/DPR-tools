#!/usr/bin/env bash
# Render Build Script for FastAPI + Prisma Backend

set -o errexit  # Exit on error

echo "Starting Render build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Generate Prisma Client
echo "Generating Prisma Client..."
prisma generate

# Run database migrations (deploy mode - no prompt)
echo "Running database migrations..."
prisma migrate deploy

# Seed the database with schemes
echo "Seeding database with schemes..."
python seed_schemes.py

echo "Build process completed successfully!"
