#!/usr/bin/env python3
"""
Migration script to make order_id nullable in payments table
This fixes the issue where payments can be created without an associated order.
"""
import psycopg2
import logging
import time
from config import get_settings
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection(settings, max_retries=3):
    """Establish database connection with retry logic"""
    parsed_url = urlparse(settings.database_url)
    
    # Extract SSL mode from query parameters
    query_params = parse_qs(parsed_url.query)
    sslmode = query_params.get('sslmode', ['prefer'])[0]
    
    connection_params = {
        'host': parsed_url.hostname,
        'port': parsed_url.port or 5432,
        'database': parsed_url.path[1:],  # Remove leading '/'
        'user': parsed_url.username,
        'password': parsed_url.password,
        'sslmode': sslmode,
        'connect_timeout': 30
    }
    
    logger.info(f"Connecting to database: {parsed_url.hostname}:{connection_params['port']}/{connection_params['database']}")
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**connection_params)
            logger.info("Database connection established successfully")
            return conn
        except psycopg2.OperationalError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"Connection attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to connect after {max_retries} attempts: {e}")
                raise

def fix_payment_order_id_nullable(dry_run=False):
    """Make order_id column nullable in payments table"""
    settings = get_settings()
    conn = None
    
    try:
        conn = get_db_connection(settings)
        cursor = conn.cursor()
        
        # Check if payments table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'payments'
            )
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            logger.error("Payments table does not exist!")
            return False
        
        # Check current order_id column constraint
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'payments' 
            AND table_schema = 'public'
            AND column_name = 'order_id'
        """)
        column_info = cursor.fetchone()
        
        if not column_info:
            logger.error("order_id column does not exist in payments table!")
            return False
        
        column_name, data_type, is_nullable = column_info
        logger.info(f"Current order_id column: type={data_type}, nullable={is_nullable}")
        
        if is_nullable == 'YES':
            logger.info("order_id column is already nullable. No migration needed.")
            return True
        
        # Make order_id nullable
        alter_sql = "ALTER TABLE payments ALTER COLUMN order_id DROP NOT NULL"
        
        if dry_run:
            logger.info(f"DRY RUN: Would execute: {alter_sql}")
            return True
        
        logger.info("Making order_id column nullable in payments table...")
        cursor.execute(alter_sql)
        conn.commit()
        logger.info("Successfully made order_id column nullable")
        
        # Verify the change
        cursor.execute("""
            SELECT is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'payments' 
            AND column_name = 'order_id'
        """)
        result = cursor.fetchone()
        if result and result[0] == 'YES':
            logger.info("✅ Migration verified: order_id column is now nullable")
        else:
            raise Exception("Migration verification failed: order_id column is still NOT NULL")
        
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Database error during migration: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    import sys
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        logger.info("Running in DRY RUN mode - no changes will be made")
    
    logger.info("=" * 60)
    logger.info("Payment Order ID Nullable Migration")
    logger.info("=" * 60)
    
    success = fix_payment_order_id_nullable(dry_run=dry_run)
    
    if success:
        logger.info("=" * 60)
        logger.info("✅ Migration completed successfully!")
        logger.info("=" * 60)
    else:
        logger.error("=" * 60)
        logger.error("❌ Migration failed!")
        logger.error("=" * 60)
    
    sys.exit(0 if success else 1)

