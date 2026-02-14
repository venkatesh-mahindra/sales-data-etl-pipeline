"""
Data Validation Module
Handles data quality checks and validation rules
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import VALIDATION_RULES, LOGGING_CONFIG

class DataValidator:
    """Validates and cleans sales data according to business rules"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        self.validation_rules = VALIDATION_RULES
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(**LOGGING_CONFIG)
    
    def validate_schema(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate DataFrame schema against required columns
        
        Args:
            df: DataFrame to validate
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        required_columns = self.validation_rules['required_columns']
        
        # Check for missing columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Check for extra columns (warning only)
        extra_columns = [col for col in df.columns if col not in required_columns and col != 'data_source']
        if extra_columns:
            self.logger.warning(f"Extra columns found: {extra_columns}")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            self.logger.info("Schema validation passed")
        else:
            self.logger.error(f"Schema validation failed: {errors}")
        
        return is_valid, errors
    
    def validate_data_types(self, df: pd.DataFrame) -> Tuple[bool, pd.DataFrame, List[str]]:
        """
        Validate and correct data types
        
        Args:
            df: DataFrame to validate
            
        Returns:
            tuple: (is_valid, corrected_df, error_messages)
        """
        errors = []
        df_corrected = df.copy()
        
        try:
            # Convert numeric columns
            numeric_columns = self.validation_rules['numeric_columns']
            for col in numeric_columns:
                if col in df_corrected.columns:
                    # Convert to numeric, coercing errors to NaN
                    df_corrected[col] = pd.to_numeric(df_corrected[col], errors='coerce')
                    
                    # Check for conversion failures
                    if df_corrected[col].isnull().any():
                        null_count = df_corrected[col].isnull().sum()
                        errors.append(f"Non-numeric values found in {col}: {null_count} records")
            
            # Convert date column
            if 'order_date' in df_corrected.columns:
                df_corrected['order_date'] = pd.to_datetime(
                    df_corrected['order_date'], 
                    format=self.validation_rules['date_format'],
                    errors='coerce'
                )
                
                if df_corrected['order_date'].isnull().any():
                    null_count = df_corrected['order_date'].isnull().sum()
                    errors.append(f"Invalid date format in order_date: {null_count} records")
            
            is_valid = len(errors) == 0
            
            if is_valid:
                self.logger.info("Data type validation passed")
            else:
                self.logger.warning(f"Data type validation issues: {errors}")
            
            return is_valid, df_corrected, errors
            
        except Exception as e:
            error_msg = f"Error during data type validation: {e}"
            self.logger.error(error_msg)
            return False, df, [error_msg]
    
    def validate_business_rules(self, df: pd.DataFrame) -> Tuple[bool, pd.DataFrame, List[str]]:
        """
        Validate business rules and constraints
        
        Args:
            df: DataFrame to validate
            
        Returns:
            tuple: (is_valid, filtered_df, error_messages)
        """
        errors = []
        df_filtered = df.copy()
        initial_count = len(df_filtered)
        
        try:
            # Validate minimum values
            min_values = self.validation_rules['min_values']
            
            for col, min_val in min_values.items():
                if col in df_filtered.columns:
                    # Find records violating minimum value
                    invalid_mask = df_filtered[col] < min_val
                    invalid_count = invalid_mask.sum()
                    
                    if invalid_count > 0:
                        errors.append(f"Records with {col} < {min_val}: {invalid_count}")
                        # Remove invalid records
                        df_filtered = df_filtered[~invalid_mask]
            
            # Remove duplicate orders
            if 'order_id' in df_filtered.columns:
                duplicate_count = df_filtered['order_id'].duplicated().sum()
                if duplicate_count > 0:
                    errors.append(f"Duplicate order IDs: {duplicate_count}")
                    df_filtered = df_filtered.drop_duplicates(subset=['order_id'], keep='first')
            
            # Remove completely empty rows
            empty_rows = df_filtered.isnull().all(axis=1).sum()
            if empty_rows > 0:
                errors.append(f"Completely empty rows: {empty_rows}")
                df_filtered = df_filtered.dropna(how='all')
            
            final_count = len(df_filtered)
            records_removed = initial_count - final_count
            
            is_valid = len(errors) == 0
            
            if records_removed > 0:
                self.logger.warning(f"Removed {records_removed} invalid records ({initial_count} -> {final_count})")
            
            if is_valid:
                self.logger.info("Business rules validation passed")
            else:
                self.logger.warning(f"Business rules validation issues: {errors}")
            
            return is_valid, df_filtered, errors
            
        except Exception as e:
            error_msg = f"Error during business rules validation: {e}"
            self.logger.error(error_msg)
            return False, df, [error_msg]
    
    def handle_missing_values(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Handle missing values in the dataset
        
        Args:
            df: DataFrame to process
            
        Returns:
            tuple: (cleaned_df, missing_value_summary)
        """
        df_cleaned = df.copy()
        missing_summary = {}
        
        try:
            # Check missing values before cleaning
            missing_before = df_cleaned.isnull().sum()
            missing_summary['before'] = missing_before[missing_before > 0].to_dict()
            
            # Handle missing values by column
            for col in df_cleaned.columns:
                missing_count = df_cleaned[col].isnull().sum()
                
                if missing_count > 0:
                    if col in ['quantity', 'price']:
                        # For numeric columns, fill with median
                        median_val = df_cleaned[col].median()
                        df_cleaned[col].fillna(median_val, inplace=True)
                        self.logger.info(f"Filled {missing_count} missing values in {col} with median: {median_val}")
                    
                    elif col == 'order_date':
                        # For dates, remove rows with missing dates
                        df_cleaned = df_cleaned.dropna(subset=[col])
                        self.logger.info(f"Removed {missing_count} rows with missing {col}")
                    
                    elif col in ['product', 'store_location']:
                        # For categorical columns, fill with 'Unknown'
                        df_cleaned[col].fillna('Unknown', inplace=True)
                        self.logger.info(f"Filled {missing_count} missing values in {col} with 'Unknown'")
            
            # Check missing values after cleaning
            missing_after = df_cleaned.isnull().sum()
            missing_summary['after'] = missing_after[missing_after > 0].to_dict()
            
            return df_cleaned, missing_summary
            
        except Exception as e:
            self.logger.error(f"Error handling missing values: {e}")
            return df, {'error': str(e)}
    
    def validate_dataset(self, df: pd.DataFrame) -> Tuple[bool, pd.DataFrame, Dict]:
        """
        Perform complete validation pipeline
        
        Args:
            df: DataFrame to validate
            
        Returns:
            tuple: (is_valid, validated_df, validation_report)
        """
        self.logger.info(f"Starting validation pipeline for {len(df)} records")
        
        validation_report = {
            'initial_records': len(df),
            'schema_valid': False,
            'data_types_valid': False,
            'business_rules_valid': False,
            'errors': [],
            'warnings': [],
            'final_records': 0
        }
        
        try:
            # Step 1: Schema validation
            schema_valid, schema_errors = self.validate_schema(df)
            validation_report['schema_valid'] = schema_valid
            validation_report['errors'].extend(schema_errors)
            
            if not schema_valid:
                return False, df, validation_report
            
            # Step 2: Data type validation
            types_valid, df_typed, type_errors = self.validate_data_types(df)
            validation_report['data_types_valid'] = types_valid
            validation_report['errors'].extend(type_errors)
            
            # Step 3: Business rules validation
            rules_valid, df_filtered, rule_errors = self.validate_business_rules(df_typed)
            validation_report['business_rules_valid'] = rules_valid
            validation_report['errors'].extend(rule_errors)
            
            # Step 4: Handle missing values
            df_cleaned, missing_summary = self.handle_missing_values(df_filtered)
            validation_report['missing_values'] = missing_summary
            
            # Final validation report
            validation_report['final_records'] = len(df_cleaned)
            validation_report['records_removed'] = len(df) - len(df_cleaned)
            
            # Overall validation status
            is_valid = schema_valid and types_valid and rules_valid
            
            if is_valid:
                self.logger.info(f"Validation completed successfully. {len(df_cleaned)} valid records remain.")
            else:
                self.logger.warning(f"Validation completed with issues. {len(df_cleaned)} records remain.")
            
            return is_valid, df_cleaned, validation_report
            
        except Exception as e:
            error_msg = f"Error during validation pipeline: {e}"
            self.logger.error(error_msg)
            validation_report['errors'].append(error_msg)
            return False, df, validation_report
