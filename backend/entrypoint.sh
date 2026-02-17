#!/bin/bash

# Exit on error
set -e

echo "Waiting for PostgreSQL to be ready..."

# Wait for database to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - continuing..."

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Start Django development server
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000
