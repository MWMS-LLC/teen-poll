# Fake Users Management for Teen Poll System

This directory contains scripts to manage fake users in the production database to help teens feel less lonely when they see poll results.

## Overview

The system generates 20 fake users who have answered all questions, making the results appear more populated and helping teens feel less isolated.

## Files

- **`generate_fake_users_csv.py`** - Main script to generate fake users and upload to production
- **`remove_fake_users_simple.py`** - Script to remove fake users when no longer needed

## How It Works

### 1. Generate Fake Users (CSV First Approach)

The `generate_fake_users_csv.py` script:

1. **Generates fake data in memory** - Creates 20 fake users with realistic teen birth years (2007-2012)
2. **Connects to production database** - Gets all questions and options to generate realistic responses
3. **Exports to CSV files** - Saves all data to CSV files in `fake_users_data/` directory:
   - `fake_users.csv` - User information
   - `fake_responses.csv` - Single-choice responses
   - `fake_checkbox_responses.csv` - Multi-select responses
4. **Uploads to production** - Imports all CSV data to the production database at once

This approach is much more efficient than inserting users one by one.

### 2. Remove Fake Users

The `remove_fake_users_simple.py` script removes fake users based on creation date (default: last 30 days).

## Usage

### Prerequisites

1. **Environment Variables**: Set `DATABASE_URL` environment variable
2. **Dependencies**: Install required packages (`pg8000`)

### Generate and Upload Fake Users

```bash
# Set your production database URL
export DATABASE_URL="postgresql://username:password@host:port/database"

# Run the script
python generate_fake_users_csv.py
```

The script will:
- Generate 20 fake users
- Create CSV files in `fake_users_data/` directory
- Upload everything to your production database
- Show progress and summary

### Remove Fake Users

```bash
# Set your production database URL
export DATABASE_URL="postgresql://username:password@host:port/database"

# Remove users created in last 30 days
python remove_fake_users_simple.py

# Or modify the script to change the days_old parameter
```

## When to Use

### Generate Fake Users
- **Before launching** - To populate initial results
- **During low-traffic periods** - To maintain engagement
- **For testing** - To verify results display correctly

### Remove Fake Users
- **After collecting real votes** - When you have enough genuine responses
- **Before analysis** - To clean data for research purposes
- **Periodically** - To maintain data quality

## Safety Features

- **CSV backup** - All generated data is saved to CSV files before upload
- **Transaction safety** - Database operations use transactions
- **Foreign key constraints** - Responses are automatically removed when users are deleted
- **Logging** - Detailed logs for monitoring and debugging

## Customization

### Change Number of Users
Modify the `num_users` parameter in `generate_fake_users_csv.py`:

```python
users = generate_fake_users(50)  # Generate 50 users instead of 20
```

### Change Age Range
Modify the birth year range in the script:

```python
birth_year = random.randint(2006, 2013)  # Different age range
```

### Change Removal Criteria
Modify the `days_old` parameter in `remove_fake_users_simple.py`:

```python
remove_fake_users(conn, days_old=60)  # Remove users from last 60 days
```

## Monitoring

Check the logs to see:
- How many users were generated
- How many responses were created
- Upload progress and success
- Any errors or warnings

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify `DATABASE_URL` is set correctly
   - Check network connectivity to database
   - Ensure SSL settings are correct

2. **Permission Errors**
   - Verify database user has INSERT permissions
   - Check table access rights

3. **CSV Export Errors**
   - Ensure write permissions in the backend directory
   - Check available disk space

### Getting Help

- Check the logs for detailed error messages
- Verify database schema matches expected structure
- Test with a small number of users first

## Data Structure

The generated fake users will have:
- **Realistic birth years** (2007-2012)
- **Recent creation dates** (within last 30 days)
- **Complete question responses** (all questions answered)
- **Varied response patterns** (realistic distribution)

This ensures the fake data looks natural and helps teens feel less alone when viewing poll results.
