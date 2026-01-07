#!/bin/sh

# Wait for postgres
if [ "$DATABASE_URL" ]; then
    echo "Waiting for postgres..."
    # Simple check for postgres service availability
    # Assumes "postgres" is the hostname as per docker-compose
    while ! nc -z postgres 5432; do
      sleep 0.1
    done
    echo "PostgreSQL started"
fi

# Run migrations
python manage.py migrate

exec "$@"
