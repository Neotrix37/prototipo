#!/bin/bash

# Set default port if not provided
export PORT=${PORT:-8000}

echo "Starting application on port $PORT"

# Run the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port $PORT
