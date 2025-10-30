#!/bin/bash
# Railway deployment script

# Generate Prisma Client
echo "Generating Prisma Client..."
prisma generate

# Run database migrations
echo "Running database migrations..."
prisma migrate deploy

# Seed the database if needed
echo "Seeding database..."
python seed_schemes.py || echo "Seeding skipped or completed"

echo "Build completed successfully!"
