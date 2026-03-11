#!/bin/bash
set -e

echo "=== Health1ERP Development Setup ==="

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "Starting PostgreSQL and Redis..."
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres redis

echo "Waiting for PostgreSQL..."
until docker compose exec postgres pg_isready -U postgres > /dev/null 2>&1; do
    sleep 1
done
echo "PostgreSQL is ready!"

echo "Running database migrations..."
cd backend
alembic upgrade head 2>/dev/null || echo "No migrations to run (run 'alembic revision --autogenerate' first)"

echo "Seeding database..."
cd ..
python scripts/seed_data.py 2>/dev/null || echo "Seed data may already exist"

echo ""
echo "=== Starting Backend ==="
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/api/docs"
echo ""
echo "To start frontend (in another terminal):"
echo "  cd frontend && npm install && npm run dev"
echo ""
echo "To start mobile (in another terminal):"
echo "  cd mobile && npm install && npx expo start"
echo ""

cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
