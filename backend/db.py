# backend/db.py
import os
import queue
import threading
from urllib.parse import urlparse
import pg8000
import ssl
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Create SSL context (no verification for dev)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE



class SimpleConnectionPool:
    """A simple thread-safe connection pool for PostgreSQL using pg8000."""

    def __init__(self, max_connections: int = 5):
        self.max_connections = max_connections
        self.pool = queue.Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()
        self.db_params = self._init_db_params()

    def _init_db_params(self) -> dict:
        """
        Initialize database connection parameters.

        Priority:
          1. DATABASE_URL if provided
          2. Individual DB_* environment variables
        """
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            parsed = urlparse(database_url)
            return {
                "host": parsed.hostname or "localhost",
                "port": parsed.port or 5432,
                "database": parsed.path.lstrip("/") or "postgres",
                "user": parsed.username or "postgres",
                "password": parsed.password or "",
                "ssl_context": ssl.create_default_context(),  # FIXED
            }
        else:
            use_ssl = os.getenv("USE_SSL", "false").lower() == "true"
            config = {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", 5432)),
                "database": os.getenv("DB_NAME", "postgres"),
                "user": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", ""),
                "ssl_context": ssl_context,
            }

            print("Database config in use:", config)
            print("Database URL from env:", os.getenv("DATABASE_URL"))

            return config
            

    def _create_connection(self):
        """Create a new database connection."""
        return pg8000.connect(**self.db_params)

    def get_connection(self):
        """
        Get a connection from the pool.
        Create a new one if under the limit,
        otherwise wait up to 30s for one to be returned.
        """
        try:
            return self.pool.get_nowait()
        except queue.Empty:
            with self.lock:
                if self.active_connections < self.max_connections:
                    self.active_connections += 1
                    try:
                        return self._create_connection()
                    except Exception:
                        self.active_connections -= 1
                        raise
                else:
                    return self.pool.get(timeout=30)

    def return_connection(self, conn):
        """
        Return a connection to the pool if it is still valid.
        If invalid, close it and decrease the active connection count.
        """
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            self.pool.put_nowait(conn)
        except:
            try:
                conn.close()
            except:
                pass
            with self.lock:
                self.active_connections -= 1


# ---- Global pool ----
connection_pool = SimpleConnectionPool(max_connections=5)


def db_check() -> bool:
    """
    Check if the database is reachable.
    """
    conn = None
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return True
    except Exception as e:
        print("DB connection failed:", str(e))
        return False
    finally:
        if conn:
            connection_pool.return_connection(conn)


def db_ssl_status() -> bool:
    """
    Check if SSL is enabled in the database connection.
    """
    return bool(connection_pool.db_params.get("ssl_context", False))
