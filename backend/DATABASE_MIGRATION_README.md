# Database Migration Guide

This guide explains how to use the improved database migration scripts for the School Copy Manufacturing Business Management application.

## Files Overview

- `update_database.py` - Main script to update database schema
- `migrate_payments.py` - Specific migration for payments table
- `test_db_connection.py` - Test database connectivity
- `DATABASE_MIGRATION_README.md` - This guide

## Prerequisites

1. **Environment Setup**: Ensure your `.env` file contains the correct Neon PostgreSQL URL:
   ```
   DATABASE_URL=postgresql://user:password@host.neon.tech:5432/dbname?sslmode=require
   ```

2. **Dependencies**: Install required packages:
   ```bash
   pip install psycopg2-binary sqlmodel
   ```

## Usage Instructions

### 1. Test Database Connection (Recommended First Step)

Before running any migrations, verify your database connection:

```bash
cd backend
python test_db_connection.py
```

**Expected Output:**
```
2024-01-XX XX:XX:XX - INFO - === Database Connection Test ===
2024-01-XX XX:XX:XX - INFO - Host: ep-cool-bush-a1nc2fji-pooler.ap-southeast-1.aws.neon.tech
2024-01-XX XX:XX:XX - INFO - Port: 5432
2024-01-XX XX:XX:XX - INFO - Database: neondb
2024-01-XX XX:XX:XX - INFO - Username: neondb_owner
2024-01-XX XX:XX:XX - INFO - SSL Mode: require
2024-01-XX XX:XX:XX - INFO - ✓ psycopg2 connection successful
2024-01-XX XX:XX:XX - INFO - ✅ All database connections successful!
```

### 2. Preview Changes (Dry Run)

Before applying changes, preview what will be done:

```bash
python update_database.py --dry-run
```

### 3. Run Migration

Apply the database schema updates:

```bash
python update_database.py
```

### 4. Run Individual Migration

To run only the payments table migration:

```bash
python migrate_payments.py
```

## Command Line Options

### update_database.py
- `--dry-run` - Preview changes without applying them
- `--skip-verification` - Skip database connection verification

### migrate_payments.py
- `--dry-run` - Preview migration without applying changes

## Features

### Professional Improvements Added

1. **Connection Retry Logic**: Automatic retry with exponential backoff
2. **Proper SSL Handling**: Correctly parses Neon's SSL requirements
3. **Transaction Management**: Automatic rollback on errors
4. **Comprehensive Logging**: Detailed logs instead of print statements
5. **Dry Run Mode**: Preview changes before applying
6. **Connection Verification**: Test connectivity before migrations
7. **Error Handling**: Graceful error handling with clear messages
8. **Migration Verification**: Confirms changes were applied correctly

### Security Features

- SSL mode correctly set to 'require' for Neon
- Connection timeouts to prevent hanging
- Proper credential handling (no password logging)
- Transaction rollback on failures

## Troubleshooting

### Common Issues

1. **Connection Refused Error**
   ```
   psycopg2.OperationalError: connection to server at "localhost" failed
   ```
   **Solution**: Check your DATABASE_URL in `.env` file. It should point to Neon, not localhost.

2. **SSL Connection Error**
   ```
   SSL connection has been closed unexpectedly
   ```
   **Solution**: Ensure `sslmode=require` is in your DATABASE_URL.

3. **Database Sleeping (Neon)**
   ```
   connection to server failed: Connection timed out
   ```
   **Solution**: Neon databases sleep after inactivity. The first connection may take longer.

### Verification Steps

1. **Check Environment Variables**:
   ```bash
   python -c "from config import get_settings; print(get_settings().database_url[:50])"
   ```

2. **Verify Migration Success**:
   ```bash
   python -c "
   from migrate_payments import get_db_connection
   from config import get_settings
   conn = get_db_connection(get_settings())
   cursor = conn.cursor()
   cursor.execute('SELECT column_name FROM information_schema.columns WHERE table_name = \\'payments\\'')
   print([row[0] for row in cursor.fetchall()])
   conn.close()
   "
   ```

## Migration Rollback

If you need to rollback the client_id column addition:

```sql
-- Connect to your database and run:
ALTER TABLE payments DROP COLUMN IF EXISTS client_id;
```

## Best Practices

1. **Always run dry-run first**: `python update_database.py --dry-run`
2. **Test connection before migration**: `python test_db_connection.py`
3. **Backup your database** before running migrations in production
4. **Monitor logs** for any warnings or errors
5. **Verify changes** after migration completes

## Support

If you encounter issues:

1. Check the logs for detailed error messages
2. Verify your Neon database is active
3. Ensure your DATABASE_URL is correctly formatted
4. Test the connection using `test_db_connection.py`

## Example Complete Workflow

```bash
# 1. Test connection
python test_db_connection.py

# 2. Preview changes
python update_database.py --dry-run

# 3. Apply changes
python update_database.py

# 4. Verify success (should show client_id in columns)
python -c "from migrate_payments import get_db_connection; from config import get_settings; conn = get_db_connection(get_settings()); cursor = conn.cursor(); cursor.execute('SELECT column_name FROM information_schema.columns WHERE table_name = \\'payments\\''); print([row[0] for row in cursor.fetchall()]); conn.close()"
```