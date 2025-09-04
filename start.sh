#!/bin/bash

# Set default port if not provided
export PORT=${PORT:-8000}

# Debug info
echo "Starting application on port $PORT"
echo "Database URL: $DATABASE_URL"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the FastAPI application
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level debug
