"""
CSV Extractor Module
Handles extraction of sales data from CSV files
"""

import pandas as pd
import logging
from typing import Optional
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.config import CSV_FILE_PATH, LOGGING_CONFIG

class CSVExtractor:
    """Extracts sales data from CSV files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(**LOGGING_CONFIG)
    
    def extract_csv_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Extract data from CSV file
        
        Args:
            file_path: Path to CSV file (optional, uses default if not provided)
            
        Returns:
            DataFrame containing extracted data
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            pd.errors.EmptyDataError: If CSV file is empty
            Exception: For other extraction errors
        """
        try:
            csv_path = file_path or CSV_FILE_PATH
            
            if not Path(csv_path).exists():
                raise FileNotFoundError(f"CSV file not found: {csv_path}")
            
            self.logger.info(f"Starting CSV extraction from: {csv_path}")
            
            # Read CSV file
            df = pd.read_csv(csv_path)
            
            # Log extraction details
            self.logger.info(f"Successfully extracted {len(df)} records from CSV")
            self.logger.info(f"Columns found: {list(df.columns)}")
            self.logger.info(f"Data shape: {df.shape}")
            
            # Add source column for tracking
            df['data_source'] = 'csv'
            
            return df
            
        except FileNotFoundError as e:
            self.logger.error(f"CSV file not found: {e}")
            raise
        except pd.errors.EmptyDataError as e:
            self.logger.error(f"CSV file is empty: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error extracting CSV data: {e}")
            raise
    
    def validate_csv_structure(self, df: pd.DataFrame) -> bool:
        """
        Validate basic CSV structure
        
        Args:
            df: DataFrame to validate
            
        Returns:
            bool: True if structure is valid
        """
        required_columns = ['order_id', 'customer_id', 'product', 'quantity', 'price', 'order_date']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        self.logger.info("CSV structure validation passed")
        return True
    
    def get_file_info(self, file_path: Optional[str] = None) -> dict:
        """
        Get information about the CSV file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            dict: File information
        """
        csv_path = file_path or CSV_FILE_PATH
        path = Path(csv_path)
        
        if not path.exists():
            return {'exists': False}
        
        return {
            'exists': True,
            'size_bytes': path.stat().st_size,
            'modified_time': path.stat().st_mtime,
            'file_name': path.name
        }
