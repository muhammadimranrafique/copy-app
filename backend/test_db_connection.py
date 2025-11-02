#!/usr/bin/env python3
"""
Test script to verify database connection to Neon PostgreSQL
"""
import logging
import sys
from config import get_settings
from urllib.parse import urlparse
import psycopg2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection():
    """Test database connection with detailed diagnostics"""
    try:
        settings = get_settings()
        parsed_url = urlparse(settings.database_url)
        
        logger.info("=== Database Connection Test ===")
        logger.info(f"Host: {parsed_url.hostname}")
        logger.info(f"Port: {parsed_url.port or 5432}")
        logger.info(f"Database: {parsed_url.path[1:]}")
        logger.info(f"Username: {parsed_url.username}")
        logger.info(f"SSL Mode: {'require' if 'sslmode=require' in settings.database_url else 'prefer'}")
        
        # Test with psycopg2 (same as migration script)
        logger.info("\n--- Testing psycopg2 connection ---")
        conn = psycopg2.connect(
            host=parsed_url.hostname,
            port=parsed_url.port or 5432,
            database=parsed_url.path[1:],
            user=parsed_url.username,
            password=parsed_url.password,
            sslmode='require' if 'sslmode=require' in settings.database_url else 'prefer',
            connect_timeout=30
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version(), current_database(), current_user")
        version, db_name, user = cursor.fetchone()
        
        logger.info(f"✓ psycopg2 connection successful")
        logger.info(f"  PostgreSQL version: {version[:50]}...")
        logger.info(f"  Connected to database: {db_name}")
        logger.info(f"  Connected as user: {user}")
        
        # Test table listing
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"  Existing tables: {tables}")
        
        conn.close()
        
        # Test with SQLModel engine
        logger.info("\n--- Testing SQLModel engine connection ---")
        from database import engine
        from sqlalchemy import text
        with engine.connect() as sqlmodel_conn:
            result = sqlmodel_conn.execute(text("SELECT current_database(), current_user"))
            db_name, user = result.fetchone()
            logger.info(f"✓ SQLModel engine connection successful")
            logger.info(f"  Connected to database: {db_name}")
            logger.info(f"  Connected as user: {user}")
        
        logger.info("\n✅ All database connections successful!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Database connection failed: {e}")
        logger.error("\nTroubleshooting tips:")
        logger.error("1. Check your DATABASE_URL in the .env file")
        logger.error("2. Ensure your Neon database is active (not sleeping)")
        logger.error("3. Verify your credentials are correct")
        logger.error("4. Check if your IP is allowed (Neon usually allows all IPs)")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)