#!/usr/bin/env python3
"""
Test Database Setup Script
This script helps you test database connection and run the pipeline
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing Database Connection...")
    
    try:
        from config.config import DATABASE_CONFIG, DATABASE_URL
        print(f"📋 Database Config: {DATABASE_CONFIG}")
        print(f"🔗 Database URL: mysql+pymysql://{DATABASE_CONFIG['user']}:{'*' * len(DATABASE_CONFIG['password'])}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}")
        
        # Test connection
        import pymysql
        conn = pymysql.connect(**DATABASE_CONFIG)
        print("✅ Database connection successful!")
        
        # Test database exists
        with conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES;")
            databases = [db[0] for db in cursor.fetchall()]
            if DATABASE_CONFIG['database'] in databases:
                print(f"✅ Database '{DATABASE_CONFIG['database']}' exists")
            else:
                print(f"❌ Database '{DATABASE_CONFIG['database']}' not found")
                print(f"💡 Available databases: {databases}")
        
        conn.close()
        return True
        
    except ImportError:
        print("❌ pymysql not installed. Run: pip3 install pymysql")
        return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure MySQL is running")
        print("2. Check database credentials in config/config.py")
        print("3. Verify database exists")
        return False

def test_dependencies():
    """Test all required dependencies"""
    print("\n🔍 Testing Dependencies...")
    
    dependencies = [
        ('pandas', 'pip3 install pandas'),
        ('numpy', 'pip3 install numpy'),
        ('sqlalchemy', 'pip3 install sqlalchemy'),
        ('pymysql', 'pip3 install pymysql'),
        ('requests', 'pip3 install requests'),
        ('scikit-learn', 'pip3 install scikit-learn')
    ]
    
    all_good = True
    for module, install_cmd in dependencies:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - Install with: {install_cmd}")
            all_good = False
    
    return all_good

def run_pipeline_if_ready():
    """Run pipeline if all tests pass"""
    print("\n🚀 Ready to Run Pipeline!")
    
    deps_ok = test_dependencies()
    db_ok = test_database_connection()
    
    if deps_ok and db_ok:
        print("\n✅ All checks passed! Running pipeline...")
        try:
            from main import ETLPipeline
            pipeline = ETLPipeline()
            result = pipeline.run_pipeline()
            
            if result.get('status') == 'SUCCESS':
                print("\n🎉 Pipeline completed successfully!")
                print(f"📊 Execution time: {result.get('pipeline_execution_time', 'N/A'):.2f} seconds")
            else:
                print(f"\n❌ Pipeline failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Pipeline execution failed: {e}")
    else:
        print("\n❌ Please fix the issues above before running pipeline")
        print("\n📖 For setup help, see: DATABASE_SETUP.md")

if __name__ == "__main__":
    print("=" * 60)
    print("🗄️  ETL Pipeline Database Setup Test")
    print("=" * 60)
    
    run_pipeline_if_ready()
