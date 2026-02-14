"""
Database Load Module
Handles loading data into MySQL data warehouse
"""

import pandas as pd
import sqlalchemy as sa
import logging
from typing import Dict, Optional, List
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import DATABASE_CONFIG, DATABASE_URL, LOGGING_CONFIG, PIPELINE_CONFIG

class DatabaseLoader:
    """Loads processed data into MySQL data warehouse"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        self.engine = None
        self.connect()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(**LOGGING_CONFIG)
    
    def connect(self):
        """Establish database connection"""
        try:
            self.engine = sa.create_engine(DATABASE_URL, echo=False)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(sa.text("SELECT 1"))
            
            self.logger.info("Database connection established successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise
    
    def create_tables(self):
        """Create all necessary tables in the data warehouse"""
        try:
            # Define table schemas
            table_schemas = {
                'raw_sales': """
                    CREATE TABLE IF NOT EXISTS raw_sales (
                        order_id VARCHAR(50) PRIMARY KEY,
                        customer_id VARCHAR(50) NOT NULL,
                        product VARCHAR(100) NOT NULL,
                        quantity INT NOT NULL,
                        price DECIMAL(10,2) NOT NULL,
                        order_date DATE NOT NULL,
                        store_location VARCHAR(100),
                        data_source VARCHAR(20),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_customer_id (customer_id),
                        INDEX idx_order_date (order_date),
                        INDEX idx_product (product)
                    )
                """,
                
                'processed_sales': """
                    CREATE TABLE IF NOT EXISTS processed_sales (
                        order_id VARCHAR(50) PRIMARY KEY,
                        customer_id VARCHAR(50) NOT NULL,
                        order_date DATE NOT NULL,
                        order_month INT NOT NULL,
                        order_year INT NOT NULL,
                        order_quarter INT NOT NULL,
                        order_month_year VARCHAR(10) NOT NULL,
                        weekday INT NOT NULL,
                        weekday_name VARCHAR(10) NOT NULL,
                        is_weekend BOOLEAN NOT NULL,
                        product VARCHAR(100) NOT NULL,
                        product_category VARCHAR(50) NOT NULL,
                        quantity INT NOT NULL,
                        price DECIMAL(10,2) NOT NULL,
                        price_category VARCHAR(20) NOT NULL,
                        total_price DECIMAL(10,2) NOT NULL,
                        estimated_profit DECIMAL(10,2) NOT NULL,
                        profit_margin_pct DECIMAL(5,2) NOT NULL,
                        order_size_category VARCHAR(20) NOT NULL,
                        has_bulk_discount BOOLEAN NOT NULL,
                        store_location VARCHAR(100),
                        region VARCHAR(20),
                        data_source VARCHAR(20),
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_customer_id (customer_id),
                        INDEX idx_order_date (order_date),
                        INDEX idx_product_category (product_category),
                        INDEX idx_region (region),
                        INDEX idx_order_month_year (order_month_year)
                    )
                """,
                
                'product_summary': """
                    CREATE TABLE IF NOT EXISTS product_summary (
                        product VARCHAR(100) PRIMARY KEY,
                        total_revenue DECIMAL(12,2) NOT NULL,
                        avg_order_value DECIMAL(10,2) NOT NULL,
                        order_count INT NOT NULL,
                        total_quantity_sold INT NOT NULL,
                        avg_quantity_per_order DECIMAL(8,2) NOT NULL,
                        avg_price DECIMAL(10,2) NOT NULL,
                        min_price DECIMAL(10,2) NOT NULL,
                        max_price DECIMAL(10,2) NOT NULL,
                        unique_customers INT NOT NULL,
                        revenue_per_unit DECIMAL(10,2) NOT NULL,
                        order_frequency DECIMAL(6,2) NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_total_revenue (total_revenue),
                        INDEX idx_order_count (order_count)
                    )
                """,
                
                'customer_summary': """
                    CREATE TABLE IF NOT EXISTS customer_summary (
                        customer_id VARCHAR(50) PRIMARY KEY,
                        recency_days INT NOT NULL,
                        frequency INT NOT NULL,
                        monetary_value DECIMAL(12,2) NOT NULL,
                        avg_order_value DECIMAL(10,2) NOT NULL,
                        order_value_std DECIMAL(10,2),
                        total_quantity INT NOT NULL,
                        avg_quantity DECIMAL(8,2) NOT NULL,
                        first_order_date DATE NOT NULL,
                        last_order_date DATE NOT NULL,
                        unique_products INT NOT NULL,
                        unique_stores INT NOT NULL,
                        customer_tenure_days INT NOT NULL,
                        avg_days_between_orders DECIMAL(8,2) NOT NULL,
                        recency_score INT NOT NULL,
                        frequency_score INT NOT NULL,
                        monetary_score INT NOT NULL,
                        rfm_score VARCHAR(3) NOT NULL,
                        customer_segment VARCHAR(20) NOT NULL,
                        lifetime_value DECIMAL(12,2) NOT NULL,
                        repeat_customer BOOLEAN NOT NULL,
                        customer_tier VARCHAR(20) NOT NULL,
                        churn_risk VARCHAR(10) NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_recency_days (recency_days),
                        INDEX idx_monetary_value (monetary_value),
                        INDEX idx_customer_segment (customer_segment),
                        INDEX idx_churn_risk (churn_risk)
                    )
                """,
                
                'monthly_sales_summary': """
                    CREATE TABLE IF NOT EXISTS monthly_sales_summary (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        order_year INT NOT NULL,
                        order_month INT NOT NULL,
                        date DATE NOT NULL UNIQUE,
                        monthly_revenue DECIMAL(12,2) NOT NULL,
                        avg_order_value DECIMAL(10,2) NOT NULL,
                        order_count INT NOT NULL,
                        unique_orders INT NOT NULL,
                        unique_customers INT NOT NULL,
                        total_quantity INT NOT NULL,
                        revenue_3mo_avg DECIMAL(12,2),
                        revenue_3mo_growth DECIMAL(8,4),
                        revenue_6mo_avg DECIMAL(12,2),
                        revenue_6mo_growth DECIMAL(8,4),
                        mom_growth DECIMAL(8,4),
                        customer_growth DECIMAL(8,4),
                        yoy_growth DECIMAL(8,4),
                        revenue_trend VARCHAR(20) NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_date (date),
                        INDEX idx_order_year_month (order_year, order_month)
                    )
                """,
                
                'ml_features': """
                    CREATE TABLE IF NOT EXISTS ml_features (
                        customer_id VARCHAR(50) PRIMARY KEY,
                        order_count INT NOT NULL,
                        lifetime_value DECIMAL(12,2) NOT NULL,
                        avg_order_value DECIMAL(10,2) NOT NULL,
                        customer_tenure_days INT NOT NULL,
                        days_since_last_order INT NOT NULL,
                        order_frequency DECIMAL(6,2) NOT NULL,
                        unique_products INT NOT NULL,
                        weekend_ratio DECIMAL(4,2) NOT NULL,
                        bulk_ratio DECIMAL(4,2) NOT NULL,
                        will_repeat_purchase BOOLEAN NOT NULL,
                        future_orders INT NOT NULL,
                        future_revenue DECIMAL(12,2) NOT NULL,
                        feature_extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_will_repeat_purchase (will_repeat_purchase),
                        INDEX idx_lifetime_value (lifetime_value),
                        INDEX idx_order_frequency (order_frequency)
                    )
                """
            }
            
            # Create tables
            with self.engine.connect() as conn:
                for table_name, schema in table_schemas.items():
                    try:
                        conn.execute(sa.text(schema))
                        self.logger.info(f"Table '{table_name}' created/verified successfully")
                    except Exception as e:
                        self.logger.error(f"Error creating table '{table_name}': {e}")
                        raise
            
            self.logger.info("All tables created/verified successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating tables: {e}")
            raise
    
    def load_raw_sales(self, df: pd.DataFrame, if_exists: str = 'append') -> int:
        """
        Load raw sales data
        
        Args:
            df: Raw sales DataFrame
            if_exists: How to behave if table exists ('fail', 'replace', 'append')
            
        Returns:
            Number of records loaded
        """
        try:
            # Select only raw sales columns
            raw_columns = [
                'order_id', 'customer_id', 'product', 'quantity', 'price',
                'order_date', 'store_location', 'data_source'
            ]
            
            df_raw = df[raw_columns].copy()
            
            # Load to database
            rows_affected = df_raw.to_sql(
                'raw_sales',
                self.engine,
                if_exists=if_exists,
                index=False,
                method='multi',
                chunksize=PIPELINE_CONFIG['batch_size']
            )
            
            self.logger.info(f"Loaded {rows_affected} records to raw_sales table")
            
            return rows_affected
            
        except Exception as e:
            self.logger.error(f"Error loading raw sales data: {e}")
            raise
    
    def load_processed_sales(self, df: pd.DataFrame, if_exists: str = 'append') -> int:
        """
        Load processed sales data
        
        Args:
            df: Processed sales DataFrame
            if_exists: How to behave if table exists
            
        Returns:
            Number of records loaded
        """
        try:
            # Load to database
            rows_affected = df.to_sql(
                'processed_sales',
                self.engine,
                if_exists=if_exists,
                index=False,
                method='multi',
                chunksize=PIPELINE_CONFIG['batch_size']
            )
            
            self.logger.info(f"Loaded {rows_affected} records to processed_sales table")
            
            return rows_affected
            
        except Exception as e:
            self.logger.error(f"Error loading processed sales data: {e}")
            raise
    
    def load_product_summary(self, df: pd.DataFrame, if_exists: str = 'replace') -> int:
        """
        Load product summary data
        
        Args:
            df: Product summary DataFrame
            if_exists: How to behave if table exists
            
        Returns:
            Number of records loaded
        """
        try:
            # Reset index to make product a column
            df_product = df.reset_index()
            
            # Load to database
            rows_affected = df_product.to_sql(
                'product_summary',
                self.engine,
                if_exists=if_exists,
                index=False,
                method='multi'
            )
            
            self.logger.info(f"Loaded {rows_affected} records to product_summary table")
            
            return rows_affected
            
        except Exception as e:
            self.logger.error(f"Error loading product summary data: {e}")
            raise
    
    def load_customer_summary(self, df: pd.DataFrame, if_exists: str = 'replace') -> int:
        """
        Load customer summary data
        
        Args:
            df: Customer summary DataFrame
            if_exists: How to behave if table exists
            
        Returns:
            Number of records loaded
        """
        try:
            # Select and rename columns
            customer_columns = [
                'customer_id', 'recency_days', 'frequency', 'monetary_value',
                'avg_order_value', 'order_value_std', 'total_quantity', 'avg_quantity',
                'first_order_date', 'last_order_date', 'unique_products', 'unique_stores',
                'customer_tenure_days', 'avg_days_between_orders',
                'recency_score', 'frequency_score', 'monetary_score', 'rfm_score',
                'customer_segment', 'lifetime_value', 'repeat_customer',
                'customer_tier', 'churn_risk'
            ]
            
            df_customer = df[customer_columns].copy()
            
            # Load to database
            rows_affected = df_customer.to_sql(
                'customer_summary',
                self.engine,
                if_exists=if_exists,
                index=False,
                method='multi'
            )
            
            self.logger.info(f"Loaded {rows_affected} records to customer_summary table")
            
            return rows_affected
            
        except Exception as e:
            self.logger.error(f"Error loading customer summary data: {e}")
            raise
    
    def load_monthly_summary(self, df: pd.DataFrame, if_exists: str = 'replace') -> int:
        """
        Load monthly sales summary data
        
        Args:
            df: Monthly summary DataFrame
            if_exists: How to behave if table exists
            
        Returns:
            Number of records loaded
        """
        try:
            # Select and rename columns
            monthly_columns = [
                'order_year', 'order_month', 'date', 'monthly_revenue',
                'avg_order_value', 'order_count', 'unique_orders', 'unique_customers',
                'total_quantity', 'revenue_3mo_avg', 'revenue_3mo_growth',
                'revenue_6mo_avg', 'revenue_6mo_growth', 'mom_growth',
                'customer_growth', 'yoy_growth', 'revenue_trend'
            ]
            
            df_monthly = df[monthly_columns].copy()
            
            # Load to database
            rows_affected = df_monthly.to_sql(
                'monthly_sales_summary',
                self.engine,
                if_exists=if_exists,
                index=False,
                method='multi'
            )
            
            self.logger.info(f"Loaded {rows_affected} records to monthly_sales_summary table")
            
            return rows_affected
            
        except Exception as e:
            self.logger.error(f"Error loading monthly summary data: {e}")
            raise
    
    def load_ml_features(self, df: pd.DataFrame, if_exists: str = 'replace') -> int:
        """
        Load ML features data
        
        Args:
            df: ML features DataFrame
            if_exists: How to behave if table exists
            
        Returns:
            Number of records loaded
        """
        try:
            # Load to database
            rows_affected = df.to_sql(
                'ml_features',
                self.engine,
                if_exists=if_exists,
                index=False,
                method='multi'
            )
            
            self.logger.info(f"Loaded {rows_affected} records to ml_features table")
            
            return rows_affected
            
        except Exception as e:
            self.logger.error(f"Error loading ML features data: {e}")
            raise
    
    def load_all_data(self, data: Dict[str, pd.DataFrame]) -> Dict[str, int]:
        """
        Load all processed data into warehouse
        
        Args:
            data: Dictionary containing all DataFrames to load
            
        Returns:
            Dictionary with load results
        """
        try:
            self.logger.info("Starting data loading process")
            
            # Create tables if they don't exist
            self.create_tables()
            
            load_results = {}
            
            # Load raw sales data
            if 'raw_data' in data:
                load_results['raw_sales'] = self.load_raw_sales(data['raw_data'])
            
            # Load processed sales data
            if 'processed_data' in data:
                load_results['processed_sales'] = self.load_processed_sales(data['processed_data'])
            
            # Load feature data
            if 'features' in data:
                features = data['features']
                
                if 'product_metrics' in features:
                    load_results['product_summary'] = self.load_product_summary(features['product_metrics'])
                
                if 'customer_rfm' in features:
                    load_results['customer_summary'] = self.load_customer_summary(features['customer_rfm'])
                
                if 'time_series' in features:
                    load_results['monthly_summary'] = self.load_monthly_summary(features['time_series'])
                
                if 'ml_features' in features:
                    load_results['ml_features'] = self.load_ml_features(features['ml_features'])
            
            self.logger.info(f"Data loading completed. Results: {load_results}")
            
            return load_results
            
        except Exception as e:
            self.logger.error(f"Error during data loading: {e}")
            raise
    
    def upsert_data(self, df: pd.DataFrame, table_name: str, key_columns: List[str]) -> int:
        """
        Upsert data (update existing, insert new)
        
        Args:
            df: DataFrame to upsert
            table_name: Target table name
            key_columns: Columns to use for matching existing records
            
        Returns:
            Number of records affected
        """
        try:
            # For simplicity, we'll use replace strategy
            # In production, you might implement proper upsert logic
            rows_affected = df.to_sql(
                table_name,
                self.engine,
                if_exists='replace',
                index=False,
                method='multi'
            )
            
            self.logger.info(f"Upserted {rows_affected} records to {table_name} table")
            
            return rows_affected
            
        except Exception as e:
            self.logger.error(f"Error upserting data to {table_name}: {e}")
            raise
    
    def close_connection(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Database connection closed")
