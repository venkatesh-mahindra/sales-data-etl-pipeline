#!/usr/bin/env python3
"""
Interview Demo Script - Shows Business Insights from ETL Pipeline
"""

import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from extract import CSVExtractor, APIExtractor
from validate import DataValidator
from transform import DataTransformer
from features import FeatureEngineer

def run_interview_demo():
    """Run complete pipeline and show business insights"""
    
    print("🎯 INTERVIEW DEMO: Sales Data ETL Pipeline")
    print("=" * 60)
    
    # Run pipeline
    csv_extractor = CSVExtractor()
    api_extractor = APIExtractor()
    validator = DataValidator()
    transformer = DataTransformer()
    feature_engineer = FeatureEngineer()
    
    print("\n📊 1. DATA EXTRACTION")
    print("-" * 30)
    csv_data = csv_extractor.extract_csv_data()
    api_data = api_extractor.extract_api_data()
    combined_data = pd.concat([csv_data, api_data], ignore_index=True)
    print(f"✅ Extracted {len(csv_data)} records from CSV")
    print(f"✅ Extracted {len(api_data)} records from API")
    print(f"✅ Combined: {len(combined_data)} total records")
    
    print("\n🔍 2. DATA VALIDATION")
    print("-" * 30)
    is_valid, validated_data, validation_report = validator.validate_dataset(combined_data)
    print(f"✅ Validation Status: {'PASSED' if is_valid else 'ISSUES FOUND'}")
    print(f"✅ Records processed: {validation_report['final_records']}")
    print(f"✅ Records removed: {validation_report['records_removed']}")
    
    print("\n🔄 3. DATA TRANSFORMATION")
    print("-" * 30)
    transformed_data = transformer.transform_data(validated_data)
    print(f"✅ Transformed shape: {transformed_data.shape}")
    print(f"✅ Total Revenue: ${transformed_data['total_price'].sum():,.2f}")
    print(f"✅ Average Order Value: ${transformed_data['total_price'].mean():,.2f}")
    
    print("\n⚙️ 4. FEATURE ENGINEERING")
    print("-" * 30)
    features = feature_engineer.engineer_features(transformed_data)
    
    # Show product metrics
    if 'product_metrics' in features:
        product_metrics = features['product_metrics']
        print("\n🏆 TOP 5 PRODUCTS BY REVENUE:")
        top_products = product_metrics.nlargest(5, 'total_revenue')
        for idx, (product, metrics) in enumerate(top_products.iterrows(), 1):
            print(f"   {idx}. {product}: ${metrics['total_revenue']:,.2f}")
    
    # Show customer segments
    if 'customer_rfm' in features:
        customer_rfm = features['customer_rfm']
        print("\n👥 CUSTOMER SEGMENTATION:")
        segments = customer_rfm['customer_segment'].value_counts()
        for segment, count in segments.items():
            print(f"   {segment}: {count} customers")
    
    # Show time series
    if 'time_series' in features:
        time_series = features['time_series']
        print("\n📈 MONTHLY REVENUE TRENDS:")
        for _, row in time_series.sort_values(['order_year', 'order_month']).iterrows():
            print(f"   {row['order_year']}-{row['order_month']:02d}: ${row['monthly_revenue']:,.2f}")
    
    # Show ML features
    if 'ml_features' in features:
        ml_features = features['ml_features']
        print("\n🤖 ML-READY FEATURES:")
        print(f"   Customers ready for ML: {len(ml_features)}")
        print(f"   Features per customer: {len(ml_features.columns)}")
        repeat_customers = ml_features['will_repeat_purchase'].sum()
        print(f"   Predicted repeat purchases: {repeat_customers}")
    
    print("\n" + "=" * 60)
    print("🎉 PIPELINE DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print("✅ Multi-source data integration")
    print("✅ Data quality management")
    print("✅ Business intelligence")
    print("✅ Customer analytics")
    print("✅ Feature engineering")
    print("✅ ML-ready datasets")
    print("\n🚀 This demonstrates complete data engineering expertise!")

if __name__ == "__main__":
    run_interview_demo()
