# 🚀 Setup and Execution Guide

## Step 1: Install Dependencies

```bash
# Navigate to project directory
cd sales_data_pipeline

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Database Setup

### Option A: Use Docker (Recommended)
```bash
# Run MySQL with Docker
docker run --name mysql_sales -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=sales_warehouse -p 3306:3306 -d mysql:8.0

# Wait for MySQL to start (30 seconds)
```

### Option B: Local MySQL
```sql
-- Connect to MySQL and run:
CREATE DATABASE sales_warehouse;
```

## Step 3: Configure Database

Edit `config/config.py` with your database credentials:

```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'password',  # Change this
    'database': 'sales_warehouse'
}
```

## Step 4: Run the Pipeline

```bash
# Run the complete ETL pipeline
python main.py
```

## Expected Output

### Console Output:
```
============================================================
SALES DATA ETL PIPELINE STARTED
============================================================
2024-02-14 10:30:15 - __main__ - INFO - Starting data extraction phase...
2024-02-14 10:30:15 - extract.csv_extractor - INFO - Starting CSV extraction from: /path/to/sales_data.csv
2024-02-14 10:30:15 - extract.csv_extractor - INFO - Successfully extracted 50 records from CSV
2024-02-14 10:30:15 - extract.api_extractor - INFO - Starting API extraction from: https://fakestoreapi.com/products
2024-02-14 10:30:16 - extract.api_extractor - INFO - Successfully extracted 50 records from API
2024-02-14 10:30:16 - __main__ - INFO - Combining data from multiple sources...
2024-02-14 10:30:16 - __main__ - INFO - Extraction completed in 1.23 seconds
2024-02-14 10:30:16 - __main__ - INFO - Total records extracted: 100
2024-02-14 10:30:16 - __main__ - INFO - Duplicate records removed: 0

2024-02-14 10:30:16 - __main__ - INFO - Starting data validation phase...
2024-02-14 10:30:16 - validate.data_validator - INFO - Schema validation passed
2024-02-14 10:30:16 - validate.data_validator - INFO - Data type validation passed
2024-02-14 10:30:16 - validate.data_validator - INFO - Business rules validation passed
2024-02-14 10:30:16 - __main__ - INFO - Validation completed in 0.45 seconds
2024-02-14 10:30:16 - __main__ - INFO - Validation completed successfully

2024-02-14 10:30:16 - __main__ - INFO - Starting data transformation phase...
2024-02-14 10:30:16 - transform.data_transformer - INFO - Calculated total_price. Total revenue: $45,230.50, Avg order value: $452.31
2024-02-14 10:30:16 - transform.data_transformer - INFO - Extracted date features. Date range: 2024-01-15 to 2024-03-04 (49 days)
2024-02-14 10:30:17 - transform.data_transformer - INFO - Transformation completed. Final shape: (100, 22)
2024-02-14 10:30:17 - __main__ - INFO - Transformation completed in 1.23 seconds

2024-02-14 10:30:17 - __main__ - INFO - Starting feature engineering phase...
2024-02-14 10:30:17 - features.feature_engineer - INFO - Calculated product metrics for 8 products
2024-02-14 10:30:17 - features.feature_engineer - INFO - Calculated RFM metrics for 15 customers
2024-02-14 10:30:17 - features.feature_engineer - INFO - Calculated time-series features for 3 months
2024-02-14 10:30:18 - features.feature_engineer - INFO - Created ML features for 15 customers
2024-02-14 10:30:18 - __main__ - INFO - Feature engineering completed in 3.67 seconds

2024-02-14 10:30:18 - __main__ - INFO - Starting data loading phase...
2024-02-14 10:30:18 - load.database_loader - INFO - Database connection established successfully
2024-02-14 10:30:18 - load.database_loader - INFO - Table 'raw_sales' created/verified successfully
2024-02-14 10:30:18 - load.database_loader - INFO - Table 'processed_sales' created/verified successfully
2024-02-14 10:30:18 - load.database_loader - INFO - Table 'product_summary' created/verified successfully
2024-02-14 10:30:18 - load.database_loader - INFO - Table 'customer_summary' created/verified successfully
2024-02-14 10:30:18 - load.database_loader - INFO - Table 'monthly_sales_summary' created/verified successfully
2024-02-14 10:30:18 - load.database_loader - INFO - Table 'ml_features' created/verified successfully
2024-02-14 10:30:18 - load.database_loader - INFO - Loaded 100 records to raw_sales table
2024-02-14 10:30:18 - load.database_loader - INFO - Loaded 100 records to processed_sales table
2024-02-14 10:30:18 - load.database_loader - INFO - Loaded 8 records to product_summary table
2024-02-14 10:30:18 - load.database_loader - INFO - Loaded 15 records to customer_summary table
2024-02-14 10:30:18 - load.database_loader - INFO - Loaded 3 records to monthly_summary table
2024-02-14 10:30:18 - load.database_loader - INFO - Loaded 15 records to ml_features table
2024-02-14 10:30:18 - __main__ - INFO - Data loading completed in 2.89 seconds
2024-02-14 10:30:18 - __main__ - INFO - Loading results:
2024-02-14 10:30:18 - __main__ - INFO -   - raw_sales: 100 records
2024-02-14 10:30:18 - __main__ - INFO -   - processed_sales: 100 records
2024-02-14 10:30:18 - __main__ - INFO -   - product_summary: 8 records
2024-02-14 10:30:18 - __main__ - INFO -   - customer_summary: 15 records
2024-02-14 10:30:18 - __main__ - INFO -   - monthly_summary: 3 records
2024-02-14 10:30:18 - __main__ - INFO -   - ml_features: 15 records

============================================================
PIPELINE EXECUTION SUMMARY
============================================================
Total execution time: 10.58 seconds
Status: SUCCESS
Timestamp: 2024-02-14T10:30:18.123456
Records processed: 100
Records removed: 0
Total records loaded: 256
============================================================
ETL Pipeline completed successfully!

============================================================
PIPELINE EXECUTION COMPLETE
============================================================
Status: SUCCESS
Execution Time: 10.58 seconds
✅ Pipeline completed successfully!
```

## Step 5: View Database Results

Connect to MySQL and run:

```sql
-- View all tables
SHOW TABLES;

-- Check raw data
SELECT * FROM raw_sales LIMIT 5;

-- Check processed data
SELECT order_id, customer_id, product, total_price, order_date 
FROM processed_sales 
ORDER BY total_price DESC 
LIMIT 10;

-- View product performance
SELECT product, total_revenue, order_count 
FROM product_summary 
ORDER BY total_revenue DESC;

-- View customer segments
SELECT customer_segment, COUNT(*) as customer_count, 
AVG(monetary_value) as avg_value
FROM customer_summary 
GROUP BY customer_segment;
```

## Step 6: Run Analytics Queries

```bash
# Execute the analytics queries
mysql -u root -p sales_warehouse < analysis/analytics.sql
```

## Step 7: Run ML Analysis

```bash
# Start Jupyter Notebook
jupyter notebook

# Open notebooks/ml_model.ipynb and run cells
```

## Troubleshooting

### Database Connection Issues
```bash
# Check if MySQL is running
docker ps | grep mysql

# Check logs
docker logs mysql_sales
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.8+
```

### Permission Issues
```bash
# Make sure logs directory exists
mkdir -p logs

# Check file permissions
ls -la
```

## Expected Database Schema

After running, you'll have these tables:

1. **raw_sales** (100 records) - Original data
2. **processed_sales** (100 records) - Transformed data
3. **product_summary** (8 records) - Product metrics
4. **customer_summary** (15 records) - Customer RFM data
5. **monthly_sales_summary** (3 records) - Time-series data
6. **ml_features** (15 records) - Machine learning features

## Sample Analytics Output

Running the SQL queries will show:

```
+------------------+--------------+------------+----------------+-----------------+
| product          | total_revenue| order_count | avg_price      | unique_customers|
+------------------+--------------+------------+----------------+-----------------+
| Laptop           | 8999.91      | 10         | 899.99         | 8               |
| Smartphone       | 6995.00      | 10         | 699.50         | 7               |
| Tablet           | 3499.91      | 10         | 349.99         | 6               |
+------------------+--------------+------------+----------------+-----------------+

+-------------------+----------------+----------------+----------------+
| customer_segment  | customer_count| avg_value     | avg_frequency  |
+-------------------+----------------+----------------+----------------+
| Champions         | 3              | 2150.50       | 4.3            |
| Loyal Customers   | 5              | 1250.25       | 3.1            |
| New Customers     | 4              | 450.75        | 1.5            |
+-------------------+----------------+----------------+----------------+
```

This gives you a complete view of the pipeline in action! 🚀
