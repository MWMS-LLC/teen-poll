#!/bin/bash

# Deploy Fake Users to Production Database
# This script generates and uploads fake users to help teens feel less lonely

echo "🚀 Teen Poll - Fake Users Deployment Script"
echo "=========================================="

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL environment variable is not set!"
    echo "Please set it first:"
    echo "export DATABASE_URL='postgresql://username:password@host:port/database'"
    exit 1
fi

echo "✅ DATABASE_URL is set"
echo "📊 Database: $(echo $DATABASE_URL | sed 's/.*@//' | sed 's/\/.*//')"

# Check if Python script exists
if [ ! -f "generate_fake_users_csv.py" ]; then
    echo "❌ Error: generate_fake_users_csv.py not found!"
    echo "Please run this script from the backend directory"
    exit 1
fi

echo "✅ Script found"
echo ""

# Confirm before proceeding
read -p "Are you sure you want to generate and upload 20 fake users to production? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "🚀 Starting fake user generation and upload..."
echo ""

# Run the Python script
python3 generate_fake_users_csv.py

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Success! Fake users have been deployed to production."
    echo ""
    echo "📊 What was created:"
    echo "   - 20 fake users with realistic teen birth years"
    echo "   - Complete responses to all questions"
    echo "   - CSV backup files in fake_users_data/ directory"
    echo ""
    echo "💡 Next steps:"
    echo "   - Monitor the results to ensure they display correctly"
    echo "   - Remove fake users later using: python3 remove_fake_users_simple.py"
    echo ""
else
    echo ""
    echo "❌ Error: Fake user deployment failed!"
    echo "Check the logs above for details."
    exit 1
fi
