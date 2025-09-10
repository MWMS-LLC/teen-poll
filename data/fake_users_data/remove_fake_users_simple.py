#!/usr/bin/env python3
"""
Simple script to remove fake users from the production database.
Run this after collecting enough real votes to clean up the temporary fake data.
"""

import os
import pg8000
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_production_db_connection():
    """Get database connection for production using DATABASE_URL"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise Exception("DATABASE_URL environment variable is not set!")
    
    # Parse DATABASE_URL
    parsed = urlparse(database_url)
    db_params = {
        'host': parsed.hostname or "localhost",
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip("/") or "postgres",
        'user': parsed.username or "postgres",
        'password': parsed.password or "",
        'ssl_context': True
    }
    
    logger.info(f"Connecting to production database: {db_params['host']}:{db_params['port']}/{db_params['database']}")
    conn = pg8000.connect(**db_params)
    return conn

def remove_fake_users(conn, days_old=30):
    """Remove fake users and their responses"""
    cursor = conn.cursor()
    
    # Count users to be removed
    cursor.execute("""
        SELECT COUNT(*) FROM users 
        WHERE created_at >= NOW() - INTERVAL %s days
    """, (days_old,))
    users_to_remove = cursor.fetchone()[0]
    
    if users_to_remove == 0:
        logger.info("✅ No fake users found to remove")
        cursor.close()
        return
    
    logger.info(f"🗑️ Removing {users_to_remove} fake users and their responses...")
    
    # Remove users created in the last X days
    # Due to foreign key constraints, responses will be automatically deleted
    cursor.execute("""
        DELETE FROM users 
        WHERE created_at >= NOW() - INTERVAL %s days
    """, (days_old,))
    
    deleted_users = cursor.rowcount
    
    conn.commit()
    cursor.close()
    
    logger.info(f"✅ Successfully removed {deleted_users} fake users and their responses")

def main():
    """Main function to remove fake users"""
    try:
        logger.info("🚀 Starting fake user removal...")
        conn = get_production_db_connection()
        
        # Remove users created in last 30 days (adjust as needed)
        remove_fake_users(conn, days_old=30)
        
        conn.close()
        logger.info("✅ Fake user removal completed!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
