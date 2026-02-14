"""
API Extractor Module
Handles extraction of sales data from REST APIs
"""

import requests
import pandas as pd
import logging
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import API_CONFIG, LOGGING_CONFIG

class APIExtractor:
    """Extracts sales data from REST APIs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        self.session = requests.Session()
        self.session.timeout = API_CONFIG['timeout']
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(**LOGGING_CONFIG)
    
    def generate_mock_sales_data(self, num_records: int = 50) -> List[Dict]:
        """
        Generate mock sales data to simulate API response
        In real scenarios, this would make actual API calls
        
        Args:
            num_records: Number of records to generate
            
        Returns:
            List of dictionaries containing sales data
        """
        import random
        
        products = ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Smartwatch', 'Monitor', 'Keyboard', 'Mouse']
        stores = ['Online', 'Seattle', 'Portland', 'Denver', 'Miami', 'Boston', 'Atlanta', 'Minneapolis']
        
        mock_data = []
        base_date = datetime.now() - timedelta(days=90)
        
        for i in range(num_records):
            order_id = f"API{2000 + i}"
            customer_id = f"APICUST{random.randint(1, 50):03d}"
            product = random.choice(products)
            quantity = random.randint(1, 5)
            price = round(random.uniform(50.0, 1200.0), 2)
            order_date = base_date + timedelta(days=random.randint(0, 90))
            store_location = random.choice(stores)
            
            mock_data.append({
                'order_id': order_id,
                'customer_id': customer_id,
                'product': product,
                'quantity': quantity,
                'price': price,
                'order_date': order_date.strftime('%Y-%m-%d'),
                'store_location': store_location
            })
        
        return mock_data
    
    def extract_api_data(self, endpoint: Optional[str] = None) -> pd.DataFrame:
        """
        Extract data from API endpoint
        
        Args:
            endpoint: API endpoint to call (optional, uses default if not provided)
            
        Returns:
            DataFrame containing extracted data
            
        Raises:
            requests.RequestException: For API request errors
            Exception: For other extraction errors
        """
        try:
            url = f"{API_CONFIG['base_url']}{endpoint or API_CONFIG['endpoint']}"
            
            self.logger.info(f"Starting API extraction from: {url}")
            
            # For demo purposes, we'll use mock data
            # In real implementation, you would make actual API calls
            mock_data = self.generate_mock_sales_data()
            
            # Convert to DataFrame
            df = pd.DataFrame(mock_data)
            
            # Log extraction details
            self.logger.info(f"Successfully extracted {len(df)} records from API")
            self.logger.info(f"Columns found: {list(df.columns)}")
            self.logger.info(f"Data shape: {df.shape}")
            
            # Add source column for tracking
            df['data_source'] = 'api'
            
            return df
            
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error extracting API data: {e}")
            raise
    
    def make_api_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """
        Make API request with retry logic
        
        Args:
            url: API URL
            params: Query parameters
            
        Returns:
            dict: API response
        """
        max_retries = API_CONFIG['retry_attempts']
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                return response.json()
                
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                
                self.logger.warning(f"API request failed (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def validate_api_response(self, data: List[Dict]) -> bool:
        """
        Validate API response structure
        
        Args:
            data: API response data
            
        Returns:
            bool: True if structure is valid
        """
        if not data or not isinstance(data, list):
            self.logger.error("Invalid API response: expected non-empty list")
            return False
        
        required_fields = ['order_id', 'customer_id', 'product', 'quantity', 'price', 'order_date']
        
        # Check first record structure
        first_record = data[0]
        missing_fields = [field for field in required_fields if field not in first_record]
        
        if missing_fields:
            self.logger.error(f"Missing required fields in API response: {missing_fields}")
            return False
        
        self.logger.info("API response validation passed")
        return True
    
    def get_api_status(self) -> Dict:
        """
        Check API status and availability
        
        Returns:
            dict: API status information
        """
        try:
            url = API_CONFIG['base_url']
            response = self.session.get(url, timeout=5)
            
            return {
                'status': 'available',
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            }
            
        except requests.RequestException as e:
            self.logger.warning(f"API status check failed: {e}")
            return {
                'status': 'unavailable',
                'error': str(e)
            }
