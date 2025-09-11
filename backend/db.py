# backend/db.py

# Step 1. Imports
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Step 2. Load environment variables from .env (local dev only)
#         On AWS App Runner, you’ll set env vars in the console instead.
load_dotenv()

# Step 3. Read environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
USE_SSL = os.getenv("USE_SSL", "false").lower() == "true"

# Step 4. Build database URL
db_url = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Step 5. Decide connect_args (SSL or not)
connect_args = {}
if USE_SSL:
    connect_args["ssl"] = True

# Step 6. Create SQLAlchemy engine
engine = create_engine(db_url, connect_args=connect_args, echo=False)

# Step 7. Utility functions


def check_connection():
    """Return 1 if DB responds to SELECT 1."""
    with engine.connect() as conn:
        return conn.execute(text("SELECT 1")).scalar()


def get_ssl_status():
    """Return True if SSL is in use, False otherwise."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()
        """)).scalar()
        return bool(result)
