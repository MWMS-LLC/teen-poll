# main.py

# Step 1. Import needed libraries
import sys
from fastapi import FastAPI

# Step 2. Import database utilities from db.py
#    - check_connection(): runs SELECT 1
#    - get_ssl_status(): checks if SSL is in use
from backend.db import check_connection, get_ssl_status

# Step 3. Create FastAPI app instance
app = FastAPI()

# Step 4. Health check endpoint
#    AWS App Runner looks here (/health) to confirm service is alive.

@app.get("/health")
def health():
    return {"status": "ok"}

# Step 5. Python version endpoint
#    Debugging tool: lets you confirm which Python runtime is running.

@app.get("/py-version")
def py_version():
    return {"python_version": sys.version}

# Step 6. Database check endpoint
#    - Runs SELECT 1 against RDS
#    - Reports if SSL is in use

@app.get("/db-check")
def db_check():
    try:
        result = check_connection()
        ssl_status = get_ssl_status()
        return {
            "status": "ok",
            "result": result,
            "ssl_in_use": ssl_status
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# Step 7. Root endpoint
#    - Simple welcome message
#    - Lets you test "/" works after deployment


@app.get("/")
def root():
    return {"message": "teen-backend running"}
