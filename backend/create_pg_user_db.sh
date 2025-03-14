#!/bin/bash

# Usage check
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <postgres_container_name>"
    exit 1
fi

# Assign container name from argument
CONTAINER_NAME=$1

# Database credentials (modify as needed)
DB_USER="postgres"
DB_PASS="password"
DB_NAME="fastapi_db"

echo "🔄 Checking if container '$CONTAINER_NAME' is running..."
if ! docker ps --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "❌ Error: Container '$CONTAINER_NAME' is not running!"
    exit 1
fi

echo "✅ PostgreSQL container is running!"

# Execute SQL commands inside the container
echo "🚀 Creating user and database..."
docker exec -it "$CONTAINER_NAME" psql -U postgres -d postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
docker exec -it "$CONTAINER_NAME" psql -U postgres -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Grant permissions
docker exec -it "$CONTAINER_NAME" psql -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo "🎉 Database '$DB_NAME' and user '$DB_USER' created successfully!"
