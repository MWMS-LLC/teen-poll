# backend/main.py
# This file imports the actual main.py from the parent directory
# This allows AWS App Runner to use backend.main:app while keeping the actual code in the root

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the actual main module
from main import app

# Re-export the app so backend.main:app works
__all__ = ['app']
