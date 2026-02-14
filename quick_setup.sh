#!/bin/bash
# Quick Setup Script for ETL Pipeline
echo "🚀 Setting up ETL Pipeline with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first:"
    echo "   brew install docker"
    echo "   brew install docker-compose"
    echo "   Then start Docker Desktop"
    exit 1
fi

# Start MySQL container
echo "📦 Starting MySQL container..."
docker run --name mysql_sales \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=sales_warehouse \
  -p 3306:3306 \
  -d mysql:8.0

# Wait for MySQL to start
echo "⏳ Waiting for MySQL to start..."
sleep 30

# Test connection
echo "🔍 Testing database connection..."
python3 -c "
import pymysql
try:
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='password', database='sales_warehouse')
    print('✅ Database connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"

# Run pipeline
echo "🚀 Running ETL pipeline..."
python3 main.py

echo "🎉 Setup complete!"
