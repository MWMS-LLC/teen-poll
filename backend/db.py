# backend/db.py
# db.py
import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

# Create a connection pool (min 1, max 10 connections)
connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=os.environ["DATABASE_URL"]
)


# Context manager to safely get and release a connection
@contextmanager
def get_db_connection():
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)

# Execute a query using the context-managed connection
def execute_query(query: str, params: tuple = None, fetch: bool = True):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch:
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            else:
                conn.commit()
                return True
