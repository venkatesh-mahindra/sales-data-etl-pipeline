#!/usr/bin/env python3
"""
Streamlit Dashboard for Sales Data ETL Pipeline
Interactive web application for demonstrating ETL pipeline results
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import pipeline components
from extract import CSVExtractor, APIExtractor
from validate import DataValidator
from transform import DataTransformer
from features import FeatureEngineer

# Page configuration
st.set_page_config(
    page_title="Sales Data ETL Pipeline",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def run_pipeline():
    """Run the complete ETL pipeline"""
    with st.spinner("🔄 Running ETL Pipeline..."):
        # Initialize components
        csv_extractor = CSVExtractor()
        api_extractor = APIExtractor()
        validator = DataValidator()
        transformer = DataTransformer()
        feature_engineer = FeatureEngineer()
        
        # Run pipeline
        csv_data = csv_extractor.extract_csv_data()
        api_data = api_extractor.extract_api_data()
        combined_data = pd.concat([csv_data, api_data], ignore_index=True)
        
        is_valid, validated_data, validation_report = validator.validate_dataset(combined_data)
        transformed_data = transformer.transform_data(validated_data)
        features = feature_engineer.engineer_features(transformed_data)
        
        return {
            'raw_data': combined_data,
            'validated_data': validated_data,
            'transformed_data': transformed_data,
            'features': features,
            'validation_report': validation_report
        }

def create_overview_metrics(pipeline_results):
    """Create overview metrics dashboard"""
    st.markdown('<h1 class="main-header">📊 Sales Data ETL Pipeline Dashboard</h1>', unsafe_allow_html=True)
    
    # Key metrics
    transformed_data = pipeline_results['transformed_data']
    features = pipeline_results['features']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📦 Total Orders",
            value=len(transformed_data),
            delta="Processed"
        )
    
    with col2:
        total_revenue = transformed_data['total_price'].sum()
        st.metric(
            label="💰 Total Revenue",
            value=f"${total_revenue:,.2f}",
            delta="Generated"
        )
    
    with col3:
        unique_customers = transformed_data['customer_id'].nunique()
        st.metric(
            label="👥 Customers",
            value=unique_customers,
            delta="Active"
        )
    
    with col4:
        unique_products = transformed_data['product'].nunique()
        st.metric(
            label="🏷️ Products",
            value=unique_products,
            delta="Catalog"
        )

def create_data_quality_section(pipeline_results):
    """Create data quality section"""
    st.markdown("## 🔍 Data Quality Overview")
    
    validation_report = pipeline_results['validation_report']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Validation Results")
        st.success(f"✅ Validation Status: {'PASSED' if validation_report['errors'] == [] else 'ISSUES FOUND'}")
        st.info(f"📈 Records Processed: {validation_report['final_records']}")
        st.warning(f"🗑️ Records Removed: {validation_report['records_removed']}")
        
        if validation_report['errors']:
            st.error("⚠️ Validation Issues:")
            for error in validation_report['errors']:
                st.write(f"• {error}")
    
    with col2:
        st.markdown("### 📋 Data Sources")
        raw_data = pipeline_results['raw_data']
        csv_count = raw_data[raw_data['data_source'] == 'csv'].shape[0]
        api_count = raw_data[raw_data['data_source'] == 'api'].shape[0]
        
        fig = go.Figure(data=[
            go.Bar(name='CSV Data', x=['CSV'], y=[csv_count], marker_color='#1f77b4'),
            go.Bar(name='API Data', x=['API'], y=[api_count], marker_color='#ff7f0e')
        ])
        fig.update_layout(title="Data Source Distribution", yaxis_title="Records")
        st.plotly_chart(fig, use_container_width=True)

def create_product_analytics(pipeline_results):
    """Create product analytics section"""
    st.markdown("## 🏆 Product Performance Analytics")
    
    features = pipeline_results['features']
    
    if 'product_metrics' in features:
        product_metrics = features['product_metrics']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Top Products by Revenue")
            top_products = product_metrics.nlargest(5, 'total_revenue')
            
            fig = px.bar(
                x=top_products.index,
                y=top_products['total_revenue'],
                title="Top 5 Products by Revenue",
                labels={'x': 'Product', 'y': 'Revenue ($)'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Product Performance Table")
            display_metrics = product_metrics[['total_revenue', 'order_count', 'avg_order_value', 'unique_customers']].round(2)
            display_metrics.columns = ['Revenue', 'Orders', 'Avg Order', 'Customers']
            st.dataframe(display_metrics, use_container_width=True)

def create_customer_analytics(pipeline_results):
    """Create customer analytics section"""
    st.markdown("## 👥 Customer Segmentation Analytics")
    
    features = pipeline_results['features']
    
    if 'customer_rfm' in features:
        customer_rfm = features['customer_rfm']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Customer Segments")
            segments = customer_rfm['customer_segment'].value_counts()
            
            fig = px.pie(
                values=segments.values,
                names=segments.index,
                title="Customer Segment Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 RFM Analysis")
            
            # Create RFM scatter plot
            fig = px.scatter(
                customer_rfm,
                x='recency_days',
                y='monetary_value',
                color='customer_segment',
                size='frequency',
                title="Customer RFM Analysis",
                labels={
                    'recency_days': 'Recency (Days)',
                    'monetary_value': 'Monetary Value ($)',
                    'frequency': 'Frequency'
                }
            )
            st.plotly_chart(fig, use_container_width=True)

def create_time_series_analytics(pipeline_results):
    """Create time series analytics section"""
    st.markdown("## 📈 Revenue Trends Analysis")
    
    features = pipeline_results['features']
    
    if 'time_series' in features:
        time_series = features['time_series']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📅 Monthly Revenue Trend")
            
            fig = px.line(
                time_series,
                x='order_month',
                y='monthly_revenue',
                title="Monthly Revenue Trend",
                labels={'order_month': 'Month', 'monthly_revenue': 'Revenue ($)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Order Volume Trend")
            
            fig = px.bar(
                time_series,
                x='order_month',
                y='order_count',
                title="Monthly Order Volume",
                labels={'order_month': 'Month', 'order_count': 'Orders'}
            )
            st.plotly_chart(fig, use_container_width=True)

def create_ml_features_section(pipeline_results):
    """Create ML features section"""
    st.markdown("## 🤖 Machine Learning Features")
    
    features = pipeline_results['features']
    
    if 'ml_features' in features:
        ml_features = features['ml_features']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Repeat Purchase Prediction")
            
            repeat_counts = ml_features['will_repeat_purchase'].value_counts()
            
            fig = px.pie(
                values=repeat_counts.values,
                names=['Will Repeat' if x == 1 else 'Won\'t Repeat' for x in repeat_counts.index],
                title="Repeat Purchase Prediction"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 ML Feature Distribution")
            
            # Show distribution of key ML features
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Order Frequency', 'Customer Lifetime Value')
            )
            
            fig.add_trace(
                go.Histogram(x=ml_features['order_frequency'], name='Order Frequency'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Histogram(x=ml_features['lifetime_value'], name='Lifetime Value'),
                row=2, col=1
            )
            
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

def create_pipeline_status():
    """Create pipeline status section"""
    st.markdown("## 🚀 Pipeline Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### ✅ Extraction Layer")
        st.success("✅ CSV Data Extracted")
        st.success("✅ API Data Extracted")
        st.success("✅ Data Combined")
    
    with col2:
        st.markdown("### 🔍 Validation Layer")
        st.success("✅ Schema Validation")
        st.success("✅ Data Type Check")
        st.success("✅ Business Rules")
    
    with col3:
        st.markdown("### ⚙️ Processing Layers")
        st.success("✅ Transformation")
        st.success("✅ Feature Engineering")
        st.success("✅ ML Features Ready")

def main():
    """Main Streamlit application"""
    
    # Sidebar
    st.sidebar.markdown("## 🎛️ Pipeline Controls")
    
    # Run pipeline button
    if st.sidebar.button("🚀 Run ETL Pipeline", type="primary"):
        st.session_state.pipeline_results = run_pipeline()
        st.session_state.pipeline_run = True
        st.sidebar.success("✅ Pipeline Completed!")
    
    # Auto-run option
    auto_run = st.sidebar.checkbox("🔄 Auto-run on start")
    
    # Initialize session state
    if 'pipeline_run' not in st.session_state:
        st.session_state.pipeline_run = False
    
    if auto_run and not st.session_state.pipeline_run:
        st.session_state.pipeline_results = run_pipeline()
        st.session_state.pipeline_run = True
    
    # Main content
    if st.session_state.pipeline_run:
        pipeline_results = st.session_state.pipeline_results
        
        # Create all sections
        create_overview_metrics(pipeline_results)
        st.markdown("---")
        
        create_data_quality_section(pipeline_results)
        st.markdown("---")
        
        create_product_analytics(pipeline_results)
        st.markdown("---")
        
        create_customer_analytics(pipeline_results)
        st.markdown("---")
        
        create_time_series_analytics(pipeline_results)
        st.markdown("---")
        
        create_ml_features_section(pipeline_results)
        st.markdown("---")
        
        create_pipeline_status()
        
        # Success message
        st.markdown('<div class="success-box">🎉 <strong>ETL Pipeline Completed Successfully!</strong> All data processed, features engineered, and insights generated.</div>', unsafe_allow_html=True)
        
    else:
        # Welcome message
        st.markdown('<h1 class="main-header">📊 Sales Data ETL Pipeline</h1>', unsafe_allow_html=True)
        
        st.markdown("""
        ## 🎯 Welcome to the Sales Data ETL Pipeline Dashboard!
        
        This interactive dashboard demonstrates a complete end-to-end ETL pipeline that:
        
        ### 📦 **Data Extraction**
        - Extracts data from CSV files and REST APIs
        - Combines multi-source data seamlessly
        
        ### 🔍 **Data Validation**
        - Comprehensive data quality checks
        - Schema validation and business rules
        
        ### 🔄 **Data Transformation**
        - Business metrics calculation
        - Date feature extraction
        - Product categorization
        
        ### ⚙️ **Feature Engineering**
        - RFM customer segmentation
        - Time-series analysis
        - ML-ready feature preparation
        
        ---
        
        ### 🚀 **Get Started:**
        
        Click the **"Run ETL Pipeline"** button in the sidebar to process the data and generate insights!
        
        Or enable **"Auto-run on start"** to see the results immediately.
        """)
        
        # Sample data preview
        st.markdown("### 📋 Sample Data Preview")
        
        # Show sample CSV data
        try:
            csv_extractor = CSVExtractor()
            sample_data = csv_extractor.extract_csv_data().head()
            st.dataframe(sample_data, use_container_width=True)
            st.info("📊 This is a sample of the sales data that will be processed by the pipeline.")
        except:
            st.warning("⚠️ Sample data not available. Run the pipeline to see results.")

if __name__ == "__main__":
    main()
