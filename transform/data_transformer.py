"""
Data Transformation Module
Handles data transformation and business logic
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import LOGGING_CONFIG

class DataTransformer:
    """Transforms validated data into business-ready format"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(**LOGGING_CONFIG)
    
    def standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names to consistent format
        
        Args:
            df: DataFrame to standardize
            
        Returns:
            DataFrame with standardized column names
        """
        try:
            df_standardized = df.copy()
            
            # Convert column names to lowercase and replace spaces with underscores
            df_standardized.columns = df_standardized.columns.str.lower().str.replace(' ', '_')
            
            self.logger.info(f"Standardized column names: {list(df_standardized.columns)}")
            
            return df_standardized
            
        except Exception as e:
            self.logger.error(f"Error standardizing column names: {e}")
            raise
    
    def calculate_total_price(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate total price for each order (quantity × price)
        
        Args:
            df: DataFrame with quantity and price columns
            
        Returns:
            DataFrame with total_price column added
        """
        try:
            df_transformed = df.copy()
            
            # Calculate total price
            df_transformed['total_price'] = df_transformed['quantity'] * df_transformed['price']
            
            # Log statistics
            total_revenue = df_transformed['total_price'].sum()
            avg_order_value = df_transformed['total_price'].mean()
            
            self.logger.info(f"Calculated total_price. Total revenue: ${total_revenue:,.2f}, Avg order value: ${avg_order_value:,.2f}")
            
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error calculating total price: {e}")
            raise
    
    def extract_date_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract date-based features from order_date
        
        Args:
            df: DataFrame with order_date column
            
        Returns:
            DataFrame with date features added
        """
        try:
            df_transformed = df.copy()
            
            # Ensure order_date is datetime
            if not pd.api.types.is_datetime64_any_dtype(df_transformed['order_date']):
                df_transformed['order_date'] = pd.to_datetime(df_transformed['order_date'])
            
            # Extract date components
            df_transformed['order_month'] = df_transformed['order_date'].dt.month
            df_transformed['order_year'] = df_transformed['order_date'].dt.year
            df_transformed['order_quarter'] = df_transformed['order_date'].dt.quarter
            df_transformed['weekday'] = df_transformed['order_date'].dt.dayofweek  # 0=Monday, 6=Sunday
            df_transformed['weekday_name'] = df_transformed['order_date'].dt.day_name()
            df_transformed['is_weekend'] = df_transformed['weekday'].isin([5, 6])  # Saturday, Sunday
            
            # Add order month-year for grouping
            df_transformed['order_month_year'] = df_transformed['order_date'].dt.to_period('M').astype(str)
            
            # Log date range
            min_date = df_transformed['order_date'].min()
            max_date = df_transformed['order_date'].max()
            date_range = (max_date - min_date).days
            
            self.logger.info(f"Extracted date features. Date range: {min_date.date()} to {max_date.date()} ({date_range} days)")
            
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error extracting date features: {e}")
            raise
    
    def categorize_products(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Categorize products based on price ranges and types
        
        Args:
            df: DataFrame with product and price columns
            
        Returns:
            DataFrame with product categories added
        """
        try:
            df_transformed = df.copy()
            
            # Price-based categorization
            def categorize_by_price(price):
                if price < 100:
                    return 'Budget'
                elif price < 500:
                    return 'Mid-Range'
                elif price < 1000:
                    return 'Premium'
                else:
                    return 'Luxury'
            
            df_transformed['price_category'] = df_transformed['price'].apply(categorize_by_price)
            
            # Product type categorization based on product name
            def categorize_by_type(product):
                product_lower = product.lower()
                if any(keyword in product_lower for keyword in ['laptop', 'computer']):
                    return 'Computing'
                elif any(keyword in product_lower for keyword in ['phone', 'smartphone']):
                    return 'Mobile'
                elif any(keyword in product_lower for keyword in ['tablet']):
                    return 'Tablet'
                elif any(keyword in product_lower for keyword in ['headphone', 'earphone']):
                    return 'Audio'
                elif any(keyword in product_lower for keyword in ['watch']):
                    return 'Wearable'
                elif any(keyword in product_lower for keyword in ['monitor']):
                    return 'Display'
                elif any(keyword in product_lower for keyword in ['keyboard', 'mouse']):
                    return 'Accessories'
                else:
                    return 'Other'
            
            df_transformed['product_category'] = df_transformed['product'].apply(categorize_by_type)
            
            # Log category distributions
            price_dist = df_transformed['price_category'].value_counts().to_dict()
            product_dist = df_transformed['product_category'].value_counts().to_dict()
            
            self.logger.info(f"Price categories: {price_dist}")
            self.logger.info(f"Product categories: {product_dist}")
            
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error categorizing products: {e}")
            raise
    
    def calculate_order_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate order-level metrics
        
        Args:
            df: DataFrame with order data
            
        Returns:
            DataFrame with order metrics added
        """
        try:
            df_transformed = df.copy()
            
            # Calculate profit margin (assuming 30% average profit margin)
            df_transformed['estimated_profit'] = df_transformed['total_price'] * 0.3
            df_transformed['profit_margin_pct'] = 30.0  # Fixed assumption
            
            # Calculate order size category
            def categorize_order_size(total_price):
                if total_price < 200:
                    return 'Small'
                elif total_price < 1000:
                    return 'Medium'
                elif total_price < 2000:
                    return 'Large'
                else:
                    return 'Enterprise'
            
            df_transformed['order_size_category'] = df_transformed['total_price'].apply(categorize_order_size)
            
            # Calculate discount indicators (simplified - assume high quantity orders have discounts)
            df_transformed['has_bulk_discount'] = df_transformed['quantity'] > 2
            
            # Log metrics
            total_profit = df_transformed['estimated_profit'].sum()
            bulk_orders = df_transformed['has_bulk_discount'].sum()
            
            self.logger.info(f"Calculated order metrics. Total estimated profit: ${total_profit:,.2f}")
            self.logger.info(f"Bulk orders (quantity > 2): {bulk_orders}")
            
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error calculating order metrics: {e}")
            raise
    
    def standardize_store_locations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize store location names and add region information
        
        Args:
            df: DataFrame with store_location column
            
        Returns:
            DataFrame with standardized locations and regions
        """
        try:
            df_transformed = df.copy()
            
            # Standardize location names (title case, remove extra spaces)
            df_transformed['store_location'] = df_transformed['store_location'].str.title().str.strip()
            
            # Map locations to regions
            location_to_region = {
                'New York': 'Northeast',
                'Los Angeles': 'West',
                'Chicago': 'Midwest',
                'Houston': 'South',
                'Phoenix': 'West',
                'Philadelphia': 'Northeast',
                'San Antonio': 'South',
                'San Diego': 'West',
                'Dallas': 'South',
                'San Jose': 'West',
                'Austin': 'South',
                'Jacksonville': 'South',
                'Fort Worth': 'South',
                'Charlotte': 'South',
                'Columbus': 'Midwest',
                'Indianapolis': 'Midwest',
                'Seattle': 'West',
                'Portland': 'West',
                'Denver': 'West',
                'Miami': 'South',
                'Boston': 'Northeast',
                'Atlanta': 'South',
                'Minneapolis': 'Midwest',
                'Online': 'Online'
            }
            
            df_transformed['region'] = df_transformed['store_location'].map(location_to_region).fillna('Unknown')
            
            # Log location distribution
            location_dist = df_transformed['store_location'].value_counts().head(10).to_dict()
            region_dist = df_transformed['region'].value_counts().to_dict()
            
            self.logger.info(f"Top 10 locations: {location_dist}")
            self.logger.info(f"Regional distribution: {region_dist}")
            
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error standardizing store locations: {e}")
            raise
    
    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply complete transformation pipeline
        
        Args:
            df: Validated DataFrame to transform
            
        Returns:
            Transformed DataFrame with business columns
        """
        self.logger.info(f"Starting transformation pipeline for {len(df)} records")
        
        try:
            # Apply transformations in sequence
            df_transformed = df.copy()
            
            # Step 1: Standardize column names
            df_transformed = self.standardize_column_names(df_transformed)
            
            # Step 2: Calculate total price
            df_transformed = self.calculate_total_price(df_transformed)
            
            # Step 3: Extract date features
            df_transformed = self.extract_date_features(df_transformed)
            
            # Step 4: Categorize products
            df_transformed = self.categorize_products(df_transformed)
            
            # Step 5: Calculate order metrics
            df_transformed = self.calculate_order_metrics(df_transformed)
            
            # Step 6: Standardize store locations
            df_transformed = self.standardize_store_locations(df_transformed)
            
            # Reorder columns for better organization
            column_order = [
                'order_id', 'customer_id', 'order_date', 'order_month', 'order_year', 
                'order_quarter', 'order_month_year', 'weekday', 'weekday_name', 'is_weekend',
                'product', 'product_category', 'quantity', 'price', 'price_category', 
                'total_price', 'estimated_profit', 'profit_margin_pct', 'order_size_category',
                'has_bulk_discount', 'store_location', 'region', 'data_source'
            ]
            
            # Only include columns that exist
            available_columns = [col for col in column_order if col in df_transformed.columns]
            df_transformed = df_transformed[available_columns]
            
            self.logger.info(f"Transformation completed. Final shape: {df_transformed.shape}")
            self.logger.info(f"Final columns: {list(df_transformed.columns)}")
            
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error during transformation pipeline: {e}")
            raise
