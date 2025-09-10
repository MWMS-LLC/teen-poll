import sqlite3
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# SQLite database file
DATABASE_FILE = "teenpoll.db"

def get_db_connection():
    """Get a database connection using SQLite"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row  # This makes results work like dictionaries
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

@contextmanager
def get_db_cursor():
    """Context manager for database operations"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        if conn:
            conn.close()

def execute_query(query, params=None, fetch=True):
    """Execute a query and return results if fetch=True"""
    try:
        with get_db_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = cursor.fetchall()
                return [dict(row) for row in result]
            else:
                return True
                
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise

def execute_many(query, params_list):
    """Execute a query with multiple parameter sets"""
    try:
        with get_db_cursor() as cursor:
            cursor.executemany(query, params_list)
            return True
        
    except Exception as e:
        logger.error(f"Batch execution failed: {e}")
        raise

def execute_script(script):
    """Execute a SQL script containing multiple statements"""
    try:
        with get_db_cursor() as cursor:
            cursor.executescript(script)
            return True
                
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        raise
