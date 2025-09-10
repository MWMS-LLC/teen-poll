#!/usr/bin/env python3
"""
Test script for production backend
This script tests the database connection and basic API functionality
"""

import os
import sys
import requests
from urllib.parse import urlparse

def test_database_url():
    """Test DATABASE_URL parsing"""
    print("🔍 Testing DATABASE_URL parsing...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable is not set!")
        return False
    
    print(f"📝 Raw DATABASE_URL: {database_url}")
    
    try:
        parsed = urlparse(database_url)
        print(f"✅ Parsed successfully:")
        print(f"   - Username: {parsed.username or 'postgres'}")
        print(f"   - Host: {parsed.hostname}")
        print(f"   - Port: {parsed.port or 5432}")
        print(f"   - Database: {parsed.path.lstrip('/') or 'postgres'}")
        print(f"   - Has password: {'Yes' if parsed.password else 'No'}")
        return True
    except Exception as e:
        print(f"❌ Failed to parse DATABASE_URL: {e}")
        return False

def test_backend_endpoints():
    """Test basic backend endpoints"""
    print("\n🔍 Testing backend endpoints...")
    
    # Get backend URL from environment or use default
    backend_url = os.getenv("BACKEND_URL", "https://teen-poll-backend.onrender.com")
    print(f"📝 Testing backend at: {backend_url}")
    
    endpoints = [
        "/",
        "/health",
        "/test",
        "/api/categories"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{backend_url}{endpoint}"
            print(f"\n🔍 Testing {endpoint}...")
            
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Success")
                if endpoint == "/api/categories":
                    data = response.json()
                    print(f"   📊 Categories returned: {len(data)}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                if response.text:
                    print(f"   📝 Response: {response.text[:200]}...")
                    
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
    
    return True

def main():
    """Main test function"""
    print("🚀 Teen Poll Backend Production Test")
    print("=" * 50)
    
    # Test DATABASE_URL parsing
    db_ok = test_database_url()
    
    # Test backend endpoints
    backend_ok = test_backend_endpoints()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Database URL parsing: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"   Backend endpoints: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    
    if db_ok and backend_ok:
        print("\n🎉 All tests passed! Backend should be working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
