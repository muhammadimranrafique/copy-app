#!/usr/bin/env python3
"""
Script to update database schema with new Payment model changes
"""
import sys
import logging
import argparse
from database import create_db_and_tables, engine
from migrate_payments import migrate_payments_table
from config import get_settings
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_database_connection():
    """Verify database connection before running migrations"""
    try:
        settings = get_settings()
        parsed_url = urlparse(settings.database_url)
        
        logger.info(f"Verifying connection to: {parsed_url.hostname}:{parsed_url.port or 5432}")
        
        # Test connection using SQLModel engine
        from database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"Database connection verified. PostgreSQL version: {version[:50]}...")
            return True
            
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.error("Please check your DATABASE_URL in the .env file")
        return False

def main():
    parser = argparse.ArgumentParser(description='Update database schema')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying them')
    parser.add_argument('--skip-verification', action='store_true', help='Skip database connection verification')
    args = parser.parse_args()
    
    logger.info("Starting database schema update...")
    
    try:
        # Verify database connection first
        if not args.skip_verification:
            if not verify_database_connection():
                logger.error("Database connection verification failed. Aborting.")
                return False
        
        # Run migrations
        logger.info("Running payment table migration...")
        migration_success = migrate_payments_table(dry_run=args.dry_run)
        
        if not migration_success:
            logger.error("Payment table migration failed")
            return False
        
        if not args.dry_run:
            # Create/update all tables with latest schema
            logger.info("Creating/updating database tables...")
            create_db_and_tables()
            logger.info("Database tables created/updated successfully")
        else:
            logger.info("DRY RUN: Would create/update database tables")
        
        logger.info("Database schema update completed successfully!")
        return True
        
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        return False
    except Exception as e:
        logger.error(f"Database update failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)