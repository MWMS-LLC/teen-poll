#!/bin/bash

# Script to generate 20 users for checkbox_responses table
# This script sets up the environment and runs the generation

echo "🚀 Checkbox Users Generation Script"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "generate_checkbox_users.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    echo ""
    echo "Solution:"
    echo "   cd backend"
    echo "   ./run_checkbox_generation.sh"
    echo ""
    exit 1
fi

echo "✅ Script location: OK"
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL environment variable is not set"
    echo ""
    echo "Please set it first:"
    echo "   export DATABASE_URL='postgresql://username:password@host:port/database_name'"
    echo ""
    echo "Or create a .env file with:"
    echo "   echo 'DATABASE_URL=your_connection_string' > .env"
    echo ""
    echo "Then run this script again."
    echo ""
    exit 1
fi

echo "✅ DATABASE_URL: Set"
echo "🔗 Testing database connection..."
echo ""

# Test connection first
echo "🧪 Running connection test..."
python test_checkbox_connection.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎯 All tests passed! Ready to generate users."
    echo ""
    echo "📋 What will happen:"
    echo "   1. Generate 20 fake teen users (birth years 2007-2012)"
    echo "   2. Find all checkbox questions in your database"
    echo "   3. Create realistic multi-select responses for each user"
    echo "   4. Export data to CSV files for review"
    echo "   5. Upload everything to your database"
    echo ""
    
    # Ask for confirmation
    read -p "🚀 Continue with generation? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🚀 Starting generation process..."
        echo "   This may take a few minutes depending on your data size."
        echo "   You'll see detailed progress updates as it runs."
        echo ""
        echo "=" * 50
        python generate_checkbox_users.py
        echo "=" * 50
        echo ""
        echo "🎉 Generation complete! Check the output above for results."
    else
        echo ""
        echo "❌ Cancelled by user"
        echo "   You can run the generation manually with:"
        echo "   python generate_checkbox_users.py"
        exit 0
    fi
else
    echo ""
    echo "❌ Database connection failed. Please fix the issues above."
    echo ""
    echo "Common solutions:"
    echo "1. Check your DATABASE_URL format"
    echo "2. Verify database credentials"
    echo "3. Ensure database is running and accessible"
    echo "4. Check network connectivity and firewall settings"
    echo ""
    exit 1
fi
