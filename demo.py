#!/usr/bin/env python3
"""
Demo Script - Shows ETL Pipeline Output Without Database
This script demonstrates the pipeline functionality and shows expected outputs
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.append(project_root)

# Import pipeline components
from extract import CSVExtractor, APIExtractor
from validate import DataValidator
from transform import DataTransformer
from features import FeatureEngineer

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"🔹 {title}")
    print("="*60)

def print_dataframe(df, title="", max_rows=5):
    """Print DataFrame with formatting"""
    if title:
        print(f"\n📊 {title}")
        print("-" * len(title))
    
    if len(df) <= max_rows:
        print(df.to_string(index=False))
    else:
        print(df.head(max_rows).to_string(index=False))
        print(f"\n... and {len(df) - max_rows} more rows")
    
    print(f"\nShape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

def run_demo():
    """Run complete ETL pipeline demo"""
    print("🚀 SALES DATA ETL PIPELINE DEMO")
    print("=" * 60)
    print("This demo shows the pipeline processing without database connection")
    print("Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    demo_start_time = time.time()
    
    try:
        # Step 1: Extraction
        print_section("STEP 1: DATA EXTRACTION")
        
        csv_extractor = CSVExtractor()
        api_extractor = APIExtractor()
        
        print("📁 Extracting CSV data...")
        csv_data = csv_extractor.extract_csv_data()
        print_dataframe(csv_data, "CSV Data Extracted", 3)
        
        print("\n🌐 Extracting API data...")
        api_data = api_extractor.extract_api_data()
        print_dataframe(api_data, "API Data Extracted", 3)
        
        # Combine data
        print("\n🔗 Combining data sources...")
        combined_data = pd.concat([csv_data, api_data], ignore_index=True)
        print(f"✅ Combined data: {len(combined_data)} total records")
        
        # Step 2: Validation
        print_section("STEP 2: DATA VALIDATION")
        
        validator = DataValidator()
        print("🔍 Running validation pipeline...")
        
        is_valid, validated_data, validation_report = validator.validate_dataset(combined_data)
        
        print(f"✅ Validation Status: {'PASSED' if is_valid else 'ISSUES FOUND'}")
        print(f"📈 Records processed: {validation_report['final_records']}")
        print(f"🗑️  Records removed: {validation_report['records_removed']}")
        
        if validation_report['errors']:
            print("⚠️  Validation Issues:")
            for error in validation_report['errors']:
                print(f"   - {error}")
        
        print_dataframe(validated_data, "Validated Data", 3)
        
        # Step 3: Transformation
        print_section("STEP 3: DATA TRANSFORMATION")
        
        transformer = DataTransformer()
        print("🔄 Applying business transformations...")
        
        transformed_data = transformer.transform_data(validated_data)
        print_dataframe(transformed_data, "Transformed Data", 3)
        
        # Show business metrics
        print(f"\n💰 Business Metrics:")
        print(f"   Total Revenue: ${transformed_data['total_price'].sum():,.2f}")
        print(f"   Average Order Value: ${transformed_data['total_price'].mean():,.2f}")
        print(f"   Total Orders: {len(transformed_data)}")
        print(f"   Unique Customers: {transformed_data['customer_id'].nunique()}")
        print(f"   Unique Products: {transformed_data['product'].nunique()}")
        
        # Step 4: Feature Engineering
        print_section("STEP 4: FEATURE ENGINEERING")
        
        feature_engineer = FeatureEngineer()
        print("⚙️  Engineering advanced features...")
        
        features = feature_engineer.engineer_features(transformed_data)
        
        # Show product metrics
        if 'product_metrics' in features:
            print_dataframe(features['product_metrics'], "Product Performance Metrics", 5)
        
        # Show customer RFM
        if 'customer_rfm' in features:
            print_dataframe(features['customer_rfm'][['customer_id', 'recency_days', 'frequency', 'monetary_value', 'customer_segment']], 
                          "Customer RFM Analysis", 5)
        
        # Show time series
        if 'time_series' in features:
            ts_data = features['time_series']
            available_cols = ['order_year', 'order_month', 'monthly_revenue', 'order_count', 'unique_customers']
            display_cols = [col for col in available_cols if col in ts_data.columns]
            print_dataframe(ts_data[display_cols], "Monthly Sales Trends", 5)
        
        # Show ML features
        if 'ml_features' in features:
            print_dataframe(features['ml_features'], "ML-Ready Features", 5)
        
        # Step 5: Summary
        print_section("PIPELINE EXECUTION SUMMARY")
        
        execution_time = time.time() - demo_start_time
        
        print(f"⏱️  Total Execution Time: {execution_time:.2f} seconds")
        print(f"✅ Status: SUCCESS")
        print(f"📅 Timestamp: {datetime.now().isoformat()}")
        
        print(f"\n📊 Data Summary:")
        print(f"   Total Records Processed: {len(transformed_data)}")
        print(f"   Unique Customers: {transformed_data['customer_id'].nunique()}")
        print(f"   Unique Products: {transformed_data['product'].nunique()}")
        print(f"   Date Range: {transformed_data['order_date'].min().date()} to {transformed_data['order_date'].max().date()}")
        print(f"   Total Revenue: ${transformed_data['total_price'].sum():,.2f}")
        
        print(f"\n🎯 Feature Sets Created:")
        for feature_set in features.keys():
            if feature_set != 'summary':
                print(f"   - {feature_set}: {len(features[feature_set])} records")
        
        # Business Insights
        print_section("BUSINESS INSIGHTS")
        
        # Top products
        top_products = features['product_metrics'].head(3)
        print("🏆 Top 3 Products by Revenue:")
        for idx, (product, metrics) in enumerate(top_products.iterrows(), 1):
            print(f"   {idx}. {product}: ${metrics['total_revenue']:,.2f}")
        
        # Customer segments
        if 'customer_rfm' in features:
            segments = features['customer_rfm']['customer_segment'].value_counts()
            print("\n👥 Customer Segments:")
            for segment, count in segments.items():
                print(f"   {segment}: {count} customers")
        
        # Revenue trend
        if 'time_series' in features and len(features['time_series']) > 1:
            latest_month = features['time_series'].iloc[-1]
            previous_month = features['time_series'].iloc[-2] if len(features['time_series']) > 1 else None
            
            print(f"\n📈 Latest Month Performance:")
            print(f"   Month: {latest_month['order_year']}-{latest_month['order_month']:02d}")
            print(f"   Revenue: ${latest_month['monthly_revenue']:,.2f}")
            print(f"   Orders: {latest_month['order_count']}")
            print(f"   Customers: {latest_month['unique_customers']}")
            
            if previous_month is not None:
                growth = ((latest_month['monthly_revenue'] - previous_month['monthly_revenue']) / 
                          previous_month['monthly_revenue']) * 100
                print(f"   Growth: {growth:+.1f}% vs previous month")
        
        print_section("NEXT STEPS")
        print("🚀 To run with database:")
        print("   1. Setup MySQL database")
        print("   2. Update config/config.py with database credentials")
        print("   3. Run: python main.py")
        print("\n📊 To explore analytics:")
        print("   1. Connect to database")
        print("   2. Run queries from analysis/analytics.sql")
        print("   3. Open notebooks/ml_model.ipynb for ML analysis")
        
        print("\n" + "="*60)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)
