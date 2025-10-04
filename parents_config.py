# Parents-specific configuration
# This file contains all the settings needed for the parents version

# Database configuration
PARENTS_DATABASE_URL = "postgresql://postgres:NBem0YTOfN94yKqFSw5F@mwms-instance.c320aqgmywbc.us-east-2.rds.amazonaws.com:5432/parents_db?sslmode=require"

# CORS origins for parents
PARENTS_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://myworldmysay.com",
    "https://www.myworldmysay.com",
    "https://api.myworldmysay.com",
    "https://teen.myworldmysay.com",
    "https://parents.myworldmysay.com",
    "https://www.parents.myworldmysay.com"
]

# API base URL for parents frontend
PARENTS_API_BASE = "https://api.myworldmysay.com"

print("Parents configuration loaded successfully!")




