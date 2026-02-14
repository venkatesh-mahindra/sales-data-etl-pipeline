#!/usr/bin/env python3
"""
Sales Data ETL Pipeline - Main Orchestration Script (No Database Version)

This script demonstrates the complete ETL pipeline without requiring database setup.
"""

import os
import sys
import logging
import time
from datetime import datetime
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import pipeline components
from config.config import LOGGING_CONFIG, PIPELINE_CONFIG
from extract import CSVExtractor, APIExtractor
from validate import DataValidator
from transform import DataTransformer
from features import FeatureEngineer

class ETLPipelineNoDB:
    """Main ETL Pipeline Orchestrator (No Database Version)"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.pipeline_start_time = time.time()
        
        # Initialize pipeline components (except database loader)
        self.csv_extractor = CSVExtractor()
        self.api_extractor = APIExtractor()
        self.validator = DataValidator()
        self.transformer = DataTransformer()
        self.feature_engineer = FeatureEngineer()
        
        self.logger.info("=" * 60)
        self.logger.info("SALES DATA ETL PIPELINE STARTED (No DB Mode)")
        self.logger.info("=" * 60)
    
    def setup_logging(self):
        """Setup logging configuration"""
        os.makedirs(os.path.dirname(LOGGING_CONFIG['filename']), exist_ok=True)
        logging.basicConfig(**LOGGING_CONFIG)
    
    def extract_data(self):
        """Extract data from all sources"""
        self.logger.info("Starting data extraction phase...")
        extraction_start = time.time()
        
        try:
            # Extract CSV data
            self.logger.info("Extracting CSV data...")
            csv_data = self.csv_extractor.extract_csv_data()
            
            # Extract API data
            self.logger.info("Extracting API data...")
            api_data = self.api_extractor.extract_api_data()
            
            # Combine data
            self.logger.info("Combining data from multiple sources...")
            combined_data = pd.concat([csv_data, api_data], ignore_index=True)
            
            # Remove duplicates across sources
            initial_count = len(combined_data)
            combined_data = combined_data.drop_duplicates(subset=['order_id'], keep='first')
            duplicates_removed = initial_count - len(combined_data)
            
            extraction_time = time.time() - extraction_start
            self.logger.info(f"Extraction completed in {extraction_time:.2f} seconds")
            self.logger.info(f"Total records extracted: {len(combined_data)}")
            self.logger.info(f"Duplicate records removed: {duplicates_removed}")
            
            return combined_data
            
        except Exception as e:
            self.logger.error(f"Data extraction failed: {e}")
            raise
    
    def validate_data(self, data):
        """Validate and clean data"""
        self.logger.info("Starting data validation phase...")
        validation_start = time.time()
        
        try:
            # Run complete validation pipeline
            is_valid, validated_data, validation_report = self.validator.validate_dataset(data)
            
            validation_time = time.time() - validation_start
            self.logger.info(f"Validation completed in {validation_time:.2f} seconds")
            
            if is_valid:
                self.logger.info("Data validation passed successfully")
            else:
                self.logger.warning("Data validation completed with issues")
            
            # Log validation summary
            self.logger.info(f"Validation summary:")
            self.logger.info(f"  - Initial records: {validation_report['initial_records']}")
            self.logger.info(f"  - Final records: {validation_report['final_records']}")
            self.logger.info(f"  - Records removed: {validation_report['records_removed']}")
            
            return validated_data, validation_report
            
        except Exception as e:
            self.logger.error(f"Data validation failed: {e}")
            raise
    
    def transform_data(self, data):
        """Transform data with business logic"""
        self.logger.info("Starting data transformation phase...")
        transformation_start = time.time()
        
        try:
            # Apply complete transformation pipeline
            transformed_data = self.transformer.transform_data(data)
            
            transformation_time = time.time() - transformation_start
            self.logger.info(f"Transformation completed in {transformation_time:.2f} seconds")
            self.logger.info(f"Transformed data shape: {transformed_data.shape}")
            self.logger.info(f"Transformed columns: {list(transformed_data.columns)}")
            
            return transformed_data
            
        except Exception as e:
            self.logger.error(f"Data transformation failed: {e}")
            raise
    
    def engineer_features(self, data):
        """Engineer advanced features"""
        self.logger.info("Starting feature engineering phase...")
        feature_engineering_start = time.time()
        
        try:
            # Apply complete feature engineering pipeline
            features = self.feature_engineer.engineer_features(data)
            
            feature_engineering_time = time.time() - feature_engineering_start
            self.logger.info(f"Feature engineering completed in {feature_engineering_time:.2f} seconds")
            
            # Log feature summary
            if 'summary' in features:
                summary = features['summary'].iloc[0]
                self.logger.info(f"Feature engineering summary:")
                self.logger.info(f"  - Total records: {summary['total_records']}")
                self.logger.info(f"  - Unique customers: {summary['unique_customers']}")
                self.logger.info(f"  - Unique products: {summary['unique_products']}")
                self.logger.info(f"  - Date range: {summary['date_range']}")
                self.logger.info(f"  - Total revenue: ${summary['total_revenue']:,.2f}")
            
            return features
            
        except Exception as e:
            self.logger.error(f"Feature engineering failed: {e}")
            raise
    
    def simulate_data_loading(self, raw_data, processed_data, features):
        """Simulate data loading (no database)"""
        self.logger.info("Starting data loading phase (simulation)...")
        loading_start = time.time()
        
        try:
            # Simulate loading results
            load_results = {
                'raw_sales': len(raw_data),
                'processed_sales': len(processed_data),
                'product_summary': len(features.get('product_metrics', pd.DataFrame())),
                'customer_summary': len(features.get('customer_rfm', pd.DataFrame())),
                'monthly_summary': len(features.get('time_series', pd.DataFrame())),
                'ml_features': len(features.get('ml_features', pd.DataFrame()))
            }
            
            loading_time = time.time() - loading_start
            self.logger.info(f"Data loading simulation completed in {loading_time:.2f} seconds")
            
            # Log loading results
            self.logger.info("Loading results (simulated):")
            for table, records in load_results.items():
                self.logger.info(f"  - {table}: {records} records")
            
            return load_results
            
        except Exception as e:
            self.logger.error(f"Data loading simulation failed: {e}")
            raise
    
    def generate_pipeline_report(self, validation_report, load_results):
        """Generate comprehensive pipeline report"""
        self.logger.info("Generating pipeline report...")
        
        try:
            pipeline_time = time.time() - self.pipeline_start_time
            
            report = {
                'pipeline_execution_time': pipeline_time,
                'timestamp': datetime.now().isoformat(),
                'validation_summary': validation_report,
                'loading_results': load_results,
                'status': 'SUCCESS'
            }
            
            self.logger.info("=" * 60)
            self.logger.info("PIPELINE EXECUTION SUMMARY")
            self.logger.info("=" * 60)
            self.logger.info(f"Total execution time: {pipeline_time:.2f} seconds")
            self.logger.info(f"Status: {report['status']}")
            self.logger.info(f"Timestamp: {report['timestamp']}")
            
            if validation_report:
                self.logger.info(f"Records processed: {validation_report['final_records']}")
                self.logger.info(f"Records removed: {validation_report['records_removed']}")
            
            if load_results:
                total_records_loaded = sum(load_results.values())
                self.logger.info(f"Total records processed: {total_records_loaded}")
            
            self.logger.info("=" * 60)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate pipeline report: {e}")
            return {'status': 'ERROR', 'error': str(e)}
    
    def run_pipeline(self):
        """Execute complete ETL pipeline"""
        try:
            # Phase 1: Extraction
            raw_data = self.extract_data()
            
            # Phase 2: Validation
            validated_data, validation_report = self.validate_data(raw_data)
            
            # Phase 3: Transformation
            transformed_data = self.transform_data(validated_data)
            
            # Phase 4: Feature Engineering
            features = self.engineer_features(transformed_data)
            
            # Phase 5: Loading (simulated)
            load_results = self.simulate_data_loading(raw_data, transformed_data, features)
            
            # Phase 6: Reporting
            report = self.generate_pipeline_report(validation_report, load_results)
            
            self.logger.info("ETL Pipeline completed successfully!")
            return report
            
        except Exception as e:
            self.logger.error(f"ETL Pipeline failed: {e}")
            error_report = {
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'execution_time': time.time() - self.pipeline_start_time
            }
            return error_report


def main():
    """Main entry point"""
    print("Starting Sales Data ETL Pipeline (No Database Mode)...")
    
    # Create and run pipeline
    pipeline = ETLPipelineNoDB()
    result = pipeline.run_pipeline()
    
    # Print final result
    print("\n" + "=" * 60)
    print("PIPELINE EXECUTION COMPLETE")
    print("=" * 60)
    print(f"Status: {result.get('status', 'UNKNOWN')}")
    print(f"Execution Time: {result.get('pipeline_execution_time', 'N/A'):.2f} seconds")
    
    if result.get('status') == 'SUCCESS':
        print("✅ Pipeline completed successfully!")
        print("\n📊 To see database results:")
        print("   1. Setup MySQL database")
        print("   2. Update config/config.py with database credentials")
        print("   3. Run: python main.py")
        exit(0)
    else:
        print("❌ Pipeline failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        exit(1)


if __name__ == "__main__":
    main()
