Here’s a **bash script** that will automatically create a user and database inside a running PostgreSQL Docker container. The user just needs to **run the script with the container name as an argument**.  

---

### **📌 Script: `create_pg_user_db.sh`**
```bash
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
```

---

### **📌 How to Use**
1. **Make the script executable**:  
   ```bash
   chmod +x create_pg_user_db.sh
   ```

2. **Run the script with your PostgreSQL container name**:  
   ```bash
   ./create_pg_user_db.sh db
   ./create_pg_user_db.sh chatbot_auth_postgres
   ```

---
```cmd
docker exec -it chatbot_auth_postgres psql -U postgres -d fastapi_db
```
```cmd
docker exec -it chatbot_auth env | grep DATABASE_URL
```
### **📌 Explanation**
✅ **Checks if the PostgreSQL container is running**  
✅ **Creates a new user and database inside the container**  
✅ **Grants all privileges to the user on the database**  
✅ **Works dynamically with any container name**  

Let me know if you need any modifications! 🚀🔥
---
- -
---
#       ----- Error Fix -----
Your `DATABASE_URL` is using port `5544`, but PostgreSQL inside the container listens on the default `5432`.  

### **🔍 Fix: Update `DATABASE_URL` to use Port 5432**
Since the `db` service in Docker is exposing port `5544` **only for external connections**, but inside the Docker network, it still runs on **5432**, update your `.env` file:

```ini
DATABASE_URL=postgresql+asyncpg://postgres:password@chatbot_auth_postgres:5432/fastapi_db
```

### **🔄 Restart Everything**
Run the following:
```bash
docker-compose down -v  # Stops and removes containers & volumes
docker-compose up --build -d  # Rebuilds and restarts services
```

Then check logs:
```bash
docker logs chatbot_auth
docker logs chatbot_auth_postgres
```

Try connecting again and let me know if it works! 🚀