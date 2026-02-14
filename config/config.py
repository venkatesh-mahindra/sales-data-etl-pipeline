"""
Configuration file for Sales Data ETL Pipeline
Contains database connection, API settings, and other configurations
"""

import os
from datetime import datetime

# Database Configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'sales_warehouse')
}

# Database Connection String for SQLAlchemy
DATABASE_URL = f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"

# API Configuration
API_CONFIG = {
    'base_url': 'https://fakestoreapi.com',
    'endpoint': '/products',
    'timeout': 30,
    'retry_attempts': 3
}

# File Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
CSV_FILE_PATH = os.path.join(DATA_DIR, 'sales_data.csv')

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

# Data Validation Rules
VALIDATION_RULES = {
    'required_columns': ['order_id', 'customer_id', 'product', 'quantity', 'price', 'order_date'],
    'numeric_columns': ['quantity', 'price'],
    'min_values': {
        'quantity': 1,
        'price': 0.01
    },
    'date_format': '%Y-%m-%d'
}

# Feature Engineering Configuration
FEATURE_CONFIG = {
    'rfm_analysis': {
        'recency_days': 365,  # Consider last year for analysis
        'frequency_threshold': 1,
        'monetary_threshold': 0
    },
    'rolling_windows': [3, 6, 12],  # months
    'customer_segments': {
        'high_value': 1000,
        'medium_value': 500,
        'low_value': 0
    }
}

# ML Configuration
ML_CONFIG = {
    'test_size': 0.2,
    'random_state': 42,
    'target_column': 'will_repeat_purchase',
    'feature_columns': [
        'total_purchase_amount', 'total_orders', 'avg_order_value',
        'days_since_last_purchase', 'purchase_frequency'
    ]
}

# Pipeline Configuration
PIPELINE_CONFIG = {
    'batch_size': 1000,
    'incremental_load': True,
    'backup_data': True,
    'notify_on_failure': True
}
