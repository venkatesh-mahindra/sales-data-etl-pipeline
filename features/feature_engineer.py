"""
Feature Engineering Module
Creates advanced business features and RFM metrics
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import FEATURE_CONFIG, LOGGING_CONFIG

class FeatureEngineer:
    """Engineers advanced features for business analytics and ML"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        self.feature_config = FEATURE_CONFIG
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(**LOGGING_CONFIG)
    
    def calculate_product_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate product-level metrics
        
        Args:
            df: Transformed DataFrame
            
        Returns:
            DataFrame with product metrics
        """
        try:
            # Group by product to calculate metrics
            product_metrics = df.groupby('product').agg({
                'total_price': ['sum', 'mean', 'count'],
                'quantity': ['sum', 'mean'],
                'price': ['mean', 'min', 'max'],
                'order_id': 'nunique'
            }).round(2)
            
            # Flatten column names
            product_metrics.columns = [
                'total_revenue', 'avg_order_value', 'order_count',
                'total_quantity_sold', 'avg_quantity_per_order',
                'avg_price', 'min_price', 'max_price', 'unique_customers'
            ]
            
            # Calculate additional metrics
            product_metrics['revenue_per_unit'] = product_metrics['total_revenue'] / product_metrics['total_quantity_sold']
            product_metrics['order_frequency'] = product_metrics['order_count'] / product_metrics['unique_customers']
            
            # Sort by total revenue
            product_metrics = product_metrics.sort_values('total_revenue', ascending=False)
            
            self.logger.info(f"Calculated product metrics for {len(product_metrics)} products")
            
            return product_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating product metrics: {e}")
            raise
    
    def calculate_customer_rfm(self, df: pd.DataFrame, reference_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Calculate RFM (Recency, Frequency, Monetary) metrics for customers
        
        Args:
            df: Transformed DataFrame
            reference_date: Reference date for recency calculation (default: latest date in data)
            
        Returns:
            DataFrame with RFM metrics
        """
        try:
            if reference_date is None:
                reference_date = df['order_date'].max()
            
            # Ensure reference_date is datetime
            if isinstance(reference_date, str):
                reference_date = pd.to_datetime(reference_date)
            
            # Calculate Recency
            recency = df.groupby('customer_id')['order_date'].max().reset_index()
            recency['recency_days'] = (reference_date - recency['order_date']).dt.days
            recency = recency.drop('order_date', axis=1)
            
            # Calculate Frequency
            frequency = df.groupby('customer_id')['order_id'].nunique().reset_index()
            frequency.columns = ['customer_id', 'frequency']
            
            # Calculate Monetary
            monetary = df.groupby('customer_id')['total_price'].sum().reset_index()
            monetary.columns = ['customer_id', 'monetary_value']
            
            # Calculate additional customer metrics
            customer_metrics = df.groupby('customer_id').agg({
                'total_price': ['mean', 'std'],
                'quantity': ['sum', 'mean'],
                'order_date': ['min', 'max'],
                'product': 'nunique',
                'store_location': 'nunique'
            }).round(2)
            
            # Flatten column names
            customer_metrics.columns = [
                'avg_order_value', 'order_value_std',
                'total_quantity', 'avg_quantity',
                'first_order_date', 'last_order_date',
                'unique_products', 'unique_stores'
            ]
            
            # Calculate customer tenure
            customer_metrics['customer_tenure_days'] = (
                customer_metrics['last_order_date'] - customer_metrics['first_order_date']
            ).dt.days
            
            # Calculate days between orders
            order_intervals = df.groupby('customer_id')['order_date'].apply(
                lambda x: x.sort_values().diff().mean().days
            ).reset_index()
            order_intervals.columns = ['customer_id', 'avg_days_between_orders']
            
            # Merge all customer metrics
            rfm = recency.merge(frequency, on='customer_id')
            rfm = rfm.merge(monetary, on='customer_id')
            rfm = rfm.merge(customer_metrics.reset_index(), on='customer_id')
            rfm = rfm.merge(order_intervals, on='customer_id', how='left')
            
            # Fill missing avg_days_between_orders for single-order customers
            rfm['avg_days_between_orders'] = rfm['avg_days_between_orders'].fillna(
                rfm['customer_tenure_days']
            )
            
            # Calculate RFM scores (1-5 scale)
            rfm['recency_score'] = pd.qcut(rfm['recency_days'], 5, labels=[5, 4, 3, 2, 1])
            rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
            rfm['monetary_score'] = pd.qcut(rfm['monetary_value'], 5, labels=[1, 2, 3, 4, 5])
            
            # Calculate RFM segment
            rfm['rfm_score'] = (
                rfm['recency_score'].astype(str) +
                rfm['frequency_score'].astype(str) +
                rfm['monetary_score'].astype(str)
            )
            
            # Segment customers based on RFM
            def segment_customers(row):
                if row['recency_score'] >= 4 and row['frequency_score'] >= 4:
                    return 'Champions'
                elif row['recency_score'] >= 3 and row['frequency_score'] >= 3:
                    return 'Loyal Customers'
                elif row['recency_score'] >= 4 and row['frequency_score'] <= 2:
                    return 'New Customers'
                elif row['recency_score'] <= 2 and row['frequency_score'] >= 3:
                    return 'At Risk'
                elif row['recency_score'] <= 2 and row['frequency_score'] <= 2:
                    return 'Lost'
                else:
                    return 'Others'
            
            rfm['customer_segment'] = rfm.apply(segment_customers, axis=1)
            
            self.logger.info(f"Calculated RFM metrics for {len(rfm)} customers")
            
            return rfm
            
        except Exception as e:
            self.logger.error(f"Error calculating RFM metrics: {e}")
            raise
    
    def calculate_time_series_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate time-series features for trend analysis
        
        Args:
            df: Transformed DataFrame
            
        Returns:
            DataFrame with time-series features
        """
        try:
            # Monthly aggregation
            monthly_sales = df.groupby(['order_year', 'order_month']).agg({
                'total_price': ['sum', 'mean', 'count'],
                'order_id': 'nunique',
                'customer_id': 'nunique',
                'quantity': 'sum'
            }).round(2)
            
            # Flatten column names
            monthly_sales.columns = [
                'monthly_revenue', 'avg_order_value', 'order_count',
                'unique_orders', 'unique_customers', 'total_quantity'
            ]
            
            # Reset index to create date column
            monthly_sales = monthly_sales.reset_index()
            monthly_sales['date'] = pd.to_datetime(
                monthly_sales['order_year'].astype(str) + '-' + 
                monthly_sales['order_month'].astype(str) + '-01'
            )
            
            # Sort by date
            monthly_sales = monthly_sales.sort_values('date')
            
            # Calculate rolling averages and growth
            for window in [3, 6]:
                if len(monthly_sales) >= window:
                    monthly_sales[f'revenue_{window}mo_avg'] = monthly_sales['monthly_revenue'].rolling(window).mean()
                    monthly_sales[f'revenue_{window}mo_growth'] = monthly_sales['monthly_revenue'].pct_change(periods=window)
            
            # Calculate month-over-month growth
            monthly_sales['mom_growth'] = monthly_sales['monthly_revenue'].pct_change()
            monthly_sales['customer_growth'] = monthly_sales['unique_customers'].pct_change()
            
            # Calculate year-over-year growth (if data available)
            if len(monthly_sales) >= 13:
                monthly_sales['yoy_growth'] = monthly_sales['monthly_revenue'].pct_change(periods=12)
            
            # Add trend indicators
            monthly_sales['revenue_trend'] = np.where(
                monthly_sales['mom_growth'] > 0, 'Increasing', 
                np.where(monthly_sales['mom_growth'] < 0, 'Decreasing', 'Stable')
            )
            
            self.logger.info(f"Calculated time-series features for {len(monthly_sales)} months")
            
            return monthly_sales
            
        except Exception as e:
            self.logger.error(f"Error calculating time-series features: {e}")
            raise
    
    def calculate_customer_lifetime_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate customer lifetime value and predictive features
        
        Args:
            df: Transformed DataFrame
            
        Returns:
            DataFrame with customer lifetime features
        """
        try:
            # Customer purchase patterns
            customer_patterns = df.groupby('customer_id').agg({
                'order_date': ['min', 'max', 'count'],
                'total_price': ['sum', 'mean', 'std'],
                'quantity': ['sum', 'mean'],
                'product': 'nunique',
                'product_category': 'nunique',
                'store_location': 'nunique',
                'is_weekend': 'sum',
                'has_bulk_discount': 'sum'
            }).round(2)
            
            # Flatten column names
            customer_patterns.columns = [
                'first_order', 'last_order', 'order_count',
                'lifetime_value', 'avg_order_value', 'order_value_std',
                'total_quantity', 'avg_quantity',
                'unique_products', 'unique_categories', 'unique_stores',
                'weekend_orders', 'bulk_orders'
            ]
            
            # Calculate derived features
            customer_patterns['customer_tenure_days'] = (
                customer_patterns['last_order'] - customer_patterns['first_order']
            ).dt.days
            
            customer_patterns['days_since_last_order'] = (
                df['order_date'].max() - customer_patterns['last_order']
            ).dt.days
            
            customer_patterns['order_frequency'] = (
                customer_patterns['order_count'] / 
                (customer_patterns['customer_tenure_days'] / 30.44)  # Average days in month
            ).round(2)
            
            customer_patterns['weekend_ratio'] = (
                customer_patterns['weekend_orders'] / customer_patterns['order_count']
            ).round(2)
            
            customer_patterns['bulk_ratio'] = (
                customer_patterns['bulk_orders'] / customer_patterns['order_count']
            ).round(2)
            
            # Predictive features
            customer_patterns['repeat_customer'] = (customer_patterns['order_count'] > 1).astype(int)
            
            # Customer value tier
            def categorize_customer_value(ltv):
                if ltv >= 2000:
                    return 'Platinum'
                elif ltv >= 1000:
                    return 'Gold'
                elif ltv >= 500:
                    return 'Silver'
                else:
                    return 'Bronze'
            
            customer_patterns['customer_tier'] = customer_patterns['lifetime_value'].apply(categorize_customer_value)
            
            # Risk indicators
            customer_patterns['churn_risk'] = np.where(
                customer_patterns['days_since_last_order'] > 90, 'High',
                np.where(customer_patterns['days_since_last_order'] > 60, 'Medium', 'Low')
            )
            
            self.logger.info(f"Calculated lifetime features for {len(customer_patterns)} customers")
            
            return customer_patterns.reset_index()
            
        except Exception as e:
            self.logger.error(f"Error calculating customer lifetime features: {e}")
            raise
    
    def create_ml_features(self, df: pd.DataFrame, target_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Create features specifically for machine learning models
        
        Args:
            df: Transformed DataFrame
            target_date: Date to split features/target (default: 30 days before latest date)
            
        Returns:
            DataFrame with ML-ready features
        """
        try:
            if target_date is None:
                target_date = df['order_date'].max() - timedelta(days=30)
            
            # Split data into features (historical) and target period
            historical_data = df[df['order_date'] <= target_date]
            target_data = df[df['order_date'] > target_date]
            
            # Calculate features from historical data
            customer_features = self.calculate_customer_lifetime_features(historical_data)
            
            # Create target variables
            target_customers = target_data.groupby('customer_id').agg({
                'order_id': 'nunique',
                'total_price': 'sum'
            }).reset_index()
            target_customers.columns = ['customer_id', 'future_orders', 'future_revenue']
            
            # Merge features with targets
            ml_features = customer_features.merge(target_customers, on='customer_id', how='left')
            
            # Fill missing targets (customers who didn't purchase in target period)
            ml_features['future_orders'] = ml_features['future_orders'].fillna(0)
            ml_features['future_revenue'] = ml_features['future_revenue'].fillna(0)
            
            # Create binary target for classification
            ml_features['will_repeat_purchase'] = (ml_features['future_orders'] > 0).astype(int)
            
            # Create additional ML features
            ml_features['value_per_order'] = ml_features['lifetime_value'] / ml_features['order_count']
            ml_features['orders_per_month'] = ml_features['order_count'] / (ml_features['customer_tenure_days'] / 30.44)
            
            # Select and rename key features for ML
            ml_feature_columns = [
                'customer_id', 'order_count', 'lifetime_value', 'avg_order_value',
                'customer_tenure_days', 'days_since_last_order', 'order_frequency',
                'unique_products', 'weekend_ratio', 'bulk_ratio',
                'will_repeat_purchase', 'future_orders', 'future_revenue'
            ]
            
            ml_features = ml_features[ml_feature_columns]
            
            self.logger.info(f"Created ML features for {len(ml_features)} customers")
            
            return ml_features
            
        except Exception as e:
            self.logger.error(f"Error creating ML features: {e}")
            raise
    
    def engineer_features(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Apply complete feature engineering pipeline
        
        Args:
            df: Transformed DataFrame
            
        Returns:
            Dictionary containing all feature datasets
        """
        self.logger.info(f"Starting feature engineering for {len(df)} records")
        
        try:
            features = {}
            
            # Product-level features
            features['product_metrics'] = self.calculate_product_metrics(df)
            
            # Customer RFM features
            features['customer_rfm'] = self.calculate_customer_rfm(df)
            
            # Time-series features
            features['time_series'] = self.calculate_time_series_features(df)
            
            # Customer lifetime features
            features['customer_lifetime'] = self.calculate_customer_lifetime_features(df)
            
            # ML-ready features
            features['ml_features'] = self.create_ml_features(df)
            
            # Summary statistics
            summary = {
                'total_records': len(df),
                'unique_customers': df['customer_id'].nunique(),
                'unique_products': df['product'].nunique(),
                'date_range': f"{df['order_date'].min().date()} to {df['order_date'].max().date()}",
                'total_revenue': df['total_price'].sum(),
                'feature_sets_created': list(features.keys())
            }
            
            features['summary'] = pd.DataFrame([summary])
            
            self.logger.info("Feature engineering completed successfully")
            self.logger.info(f"Created feature sets: {list(features.keys())}")
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error during feature engineering: {e}")
            raise
