# backend/db.py
import os
import logging
from contextlib import contextmanager

import psycopg2
from psycopg2.pool import ThreadedConnectionPool

# Load .env locally; no effect in prod if env vars are already set
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional in prod; ignore if not installed
    pass

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment or .env file")

# Create a connection pool once at startup
try:
    connection_pool = ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        dsn=DATABASE_URL,
        options="-c client_encoding=utf8"
    )
except Exception as e:
    logger.error(f"Error creating connection pool: {e}")
    raise

@contextmanager
def get_db_connection():
    """Yield a pooled connection and always return it to the pool."""
    conn = None
    try:
        conn = connection_pool.getconn()
        yield conn
    finally:
        if conn is not None:
            connection_pool.putconn(conn)

def db_check():
    """Return True if SELECT 1 succeeds."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                return cur.fetchone()[0] == 1
    except Exception as e:
        logger.error(f"DB check failed: {e}")
        return False

def db_ssl_status():
    """Return server 'ssl' setting (e.g., 'on' or 'off')."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SHOW ssl;")
                return cur.fetchone()[0]
    except Exception as e:
        logger.error(f"Failed to check SSL status: {e}")
        return None

