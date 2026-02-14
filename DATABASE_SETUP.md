# 🗄️ Database Setup Guide for ETL Pipeline

## 🚀 Option 1: Docker Setup (Recommended)

### Step 1: Install Docker
```bash
# On Mac with Homebrew
brew install docker
brew install docker-compose

# Start Docker Desktop
open /Applications/Docker.app
```

### Step 2: Run MySQL Container
```bash
# Create and start MySQL container
docker run --name mysql_sales \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=sales_warehouse \
  -p 3306:3306 \
  -d mysql:8.0

# Verify container is running
docker ps | grep mysql_sales
```

### Step 3: Update Configuration
Edit `config/config.py` with these settings:
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'password',
    'database': 'sales_warehouse'
}
```

## 🍎 Option 2: Local MySQL Installation

### Step 1: Install MySQL
```bash
# On Mac with Homebrew
brew install mysql
brew services start mysql

# Set root password
mysql_secure_installation
```

### Step 2: Create Database
```sql
# Connect to MySQL
mysql -u root -p

# Create database
CREATE DATABASE sales_warehouse;

# Create user (optional)
CREATE USER 'etl_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON sales_warehouse.* TO 'etl_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 3: Update Configuration
Edit `config/config.py`:
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',  # or 'etl_user'
    'password': 'your_password',  # your actual password
    'database': 'sales_warehouse'
}
```

## 🏃‍♂️ Step 4: Run the Pipeline

### Test Database Connection
```bash
cd sales_data_pipeline
python3 -c "
from config.config import DATABASE_CONFIG
print('Database Config:', DATABASE_CONFIG)
try:
    import pymysql
    conn = pymysql.connect(**DATABASE_CONFIG)
    print('✅ Database connection successful!')
    conn.close()
except Exception as e:
    print('❌ Connection failed:', e)
"
```

### Run Pipeline
```bash
python3 pipeline_demo.py
```

## 📊 Expected Output with Database

```
============================================================
SALES DATA ETL PIPELINE STARTED
============================================================
2024-02-14 15:30:15 - load.database_loader - INFO - Database connection established successfully
2024-02-14 15:30:15 - load.database_loader - INFO - Table 'raw_sales' created/verified successfully
2024-02-14 15:30:15 - load.database_loader - INFO - Table 'processed_sales' created/verified successfully
2024-02-14 15:30:15 - load.database_loader - INFO - Table 'product_summary' created/verified successfully
2024-02-14 15:30:15 - load.database_loader - INFO - Table 'customer_summary' created/verified successfully
2024-02-14 15:30:15 - load.database_loader - INFO - Table 'monthly_sales_summary' created/verified successfully
2024-02-14 15:30:15 - load.database_loader - INFO - Table 'ml_features' created/verified successfully
2024-02-14 15:30:16 - load.database_loader - INFO - Loaded 100 records to raw_sales table
2024-02-14 15:30:16 - load.database_loader - INFO - Loaded 100 records to processed_sales table
2024-02-14 15:30:16 - load.database_loader - INFO - Loaded 8 records to product_summary table
2024-02-14 15:30:16 - load.database_loader - INFO - Loaded 46 records to customer_summary table
2024-02-14 15:30:16 - load.database_loader - INFO - Loaded 7 records to monthly_summary table
2024-02-14 15:30:16 - load.database_loader - INFO - Loaded 41 records to ml_features table
============================================================
PIPELINE EXECUTION SUMMARY
============================================================
Total execution time: 12.58 seconds
Status: SUCCESS
Total records loaded: 302
============================================================
✅ Pipeline completed successfully!
```

## 🔍 Step 5: Explore Analytics

### Connect to Database
```bash
# Using MySQL command line
mysql -u root -p sales_warehouse

# Or using Python
python3 -c "
import pandas as pd
from sqlalchemy import create_text
from config.config import DATABASE_URL
from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL)

# Show tables
tables = pd.read_sql('SHOW TABLES', engine)
print('Tables:', tables)

# Sample query
sample = pd.read_sql('SELECT * FROM product_summary LIMIT 5', engine)
print('Product Summary:')
print(sample)
"
```

### Run Analytics Queries
```bash
# Execute all analytics queries
mysql -u root -p sales_warehouse < analysis/analytics.sql

# Or run individual queries
mysql -u root -p sales_warehouse -e "
SELECT product, total_revenue 
FROM product_summary 
ORDER BY total_revenue DESC 
LIMIT 5;
"
```

## 📓 Step 6: Run ML Analysis

### Start Jupyter Notebook
```bash
# Install Jupyter if not installed
pip3 install jupyter

# Start notebook server
jupyter notebook

# Open notebooks/ml_model.ipynb in your browser
# Run cells sequentially to see ML results
```

## 🔧 Troubleshooting

### Connection Issues
```bash
# Check if MySQL is running
docker ps | grep mysql_sales
# OR
brew services list | grep mysql

# Check logs
docker logs mysql_sales
# OR
tail -f /usr/local/var/mysql/mysql.log
```

### Permission Issues
```bash
# Reset MySQL root password
brew services stop mysql
mysqld_safe --skip-grant-tables &
mysql -u root
UPDATE mysql.user SET authentication_string='' WHERE User='root';
FLUSH PRIVILEGES;
EXIT;
brew services start mysql
```

### Port Conflicts
```bash
# Check if port 3306 is in use
lsof -i :3306

# Use different port in config
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3307,  # Change this
    ...
}
```

## 🎯 Success Indicators

✅ **Database Connection**: "Database connection established successfully"  
✅ **Table Creation**: All 6 tables created/verified  
✅ **Data Loading**: Records loaded to all tables  
✅ **Analytics**: SQL queries return results  
✅ **ML Notebook**: Models train successfully  

## 📈 Database Schema Created

After successful run, you'll have these tables:

| Table | Records | Purpose |
|-------|---------|---------|
| `raw_sales` | 100 | Original data from sources |
| `processed_sales` | 100 | Transformed data with business metrics |
| `product_summary` | 8 | Product performance metrics |
| `customer_summary` | 46 | Customer RFM analysis |
| `monthly_sales_summary` | 7 | Time-series trends |
| `ml_features` | 41 | ML-ready features |

## 🚀 Ready for Production!

Once you successfully run with database, you have a complete production-ready ETL pipeline that:
- Processes multi-source data
- Ensures data quality
- Creates business insights
- Prepares ML features
- Stores results in a proper data warehouse

This demonstrates full-stack data engineering expertise! 🎉
