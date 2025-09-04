#!/bin/bash

# Set default port if not provided
export PORT=${PORT:-8000}

# Debug info
echo "Starting application on port $PORT"
echo "Database URL: $DATABASE_URL"

# Wait for database to be ready (useful for containerized environments)
echo "Waiting for database to be ready..."
until PGPASSWORD=${DATABASE_URL##*:} psql -h "${DATABASE_URL##*@}" -U "${DATABASE_URL##*//}" -d "${DATABASE_URL##*/}" -c "SELECT 1" > /dev/null 2>&1; do
  echo "Waiting for database..."
  sleep 1
done

echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the FastAPI application
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level debug
