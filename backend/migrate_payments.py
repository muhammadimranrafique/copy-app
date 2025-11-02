#!/usr/bin/env python3
"""
Migration script to add client_id column to payments table
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

def migrate_payments_table(dry_run=False):
    """Migrate payments table with client_id column"""
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
            logger.info("Payments table does not exist yet. Will be created by create_db_and_tables()")
            return True
        
        # Check current table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'payments' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        logger.info(f"Current payments table columns: {[col[0] for col in columns]}")
        
        column_names = [col[0] for col in columns]
        
        if 'client_id' not in column_names:
            # Check if clients table exists for foreign key
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'clients'
                )
            """)
            clients_table_exists = cursor.fetchone()[0]
            
            if not clients_table_exists:
                logger.warning("Clients table does not exist. Creating client_id column without foreign key constraint.")
                alter_sql = "ALTER TABLE payments ADD COLUMN client_id UUID"
            else:
                alter_sql = "ALTER TABLE payments ADD COLUMN client_id UUID REFERENCES clients(id)"
            
            if dry_run:
                logger.info(f"DRY RUN: Would execute: {alter_sql}")
                return True
            
            logger.info("Adding client_id column to payments table...")
            cursor.execute(alter_sql)
            conn.commit()
            logger.info("Successfully added client_id column to payments table")
            
            # Verify the change
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'payments' AND column_name = 'client_id'
            """)
            if cursor.fetchone():
                logger.info("Migration verified: client_id column exists")
            else:
                raise Exception("Migration verification failed: client_id column not found")
        else:
            logger.info("client_id column already exists in payments table")
        
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
    
    success = migrate_payments_table(dry_run=dry_run)
    sys.exit(0 if success else 1)