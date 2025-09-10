# Checkbox Users Generation Script

This script generates 20 fake users specifically for the `checkbox_responses` table in your Teen Poll application.

## What it does

1. **Generates 20 fake users** with random birth years (2007-2012) and creation dates
2. **Finds all checkbox questions** from your database (questions where `check_box = TRUE`)
3. **Creates realistic responses** for each user across all checkbox questions
4. **Exports data to CSV** files for review before upload
5. **Uploads to database** the users and their checkbox responses

## Prerequisites

1. **Database connection**: Set your `DATABASE_URL` environment variable
2. **Python dependencies**: Install required packages
3. **Database schema**: Ensure your database has the required tables

## Setup

1. **Set environment variable**:
   ```bash
   export DATABASE_URL="postgresql://username:password@host:port/database_name"
   ```

2. **Install dependencies** (if not already installed):
   ```bash
   pip install pg8000
   ```

## Usage

### Option 1: Run directly
```bash
cd backend
python generate_checkbox_users.py
```

### Option 2: Generate CSV only (without database upload)
```bash
cd backend
python -c "
import generate_checkbox_users
generate_checkbox_users.main()
"
```

## Output

The script will create:
- `checkbox_users_data/checkbox_users.csv` - 20 fake users
- `checkbox_users_data/checkbox_responses.csv` - all checkbox responses

## Database Tables Used

- `users` - stores the generated fake users
- `questions` - gets checkbox questions (where check_box = TRUE)
- `options` - gets available options for each question
- `checkbox_responses` - stores the multi-select responses

## Features

- **Realistic data**: Random but sensible responses
- **Multi-select support**: Respects `max_select` limits
- **Weighted responses**: Random weights between 0.5-1.5
- **CSV export**: Review data before database upload
- **Error handling**: Comprehensive logging and error reporting
- **Teen demographics**: Birth years 2007-2012 (ages 11-16)

## Customization

You can modify the script to:
- Change the number of users (default: 20)
- Adjust birth year ranges
- Modify response patterns
- Change weight ranges
- Add more realistic response logic

## Troubleshooting

- **Connection errors**: Check your `DATABASE_URL` environment variable
- **Missing tables**: Ensure your database schema is set up correctly
- **Permission errors**: Verify database user has INSERT permissions
- **CSV export issues**: Check write permissions in the backend directory

## Example Output

```
🚀 Starting checkbox users generation...
Generating 20 fake users...
Connecting to database to get checkbox questions...
📝 Found 15 checkbox questions
Generating checkbox responses for all users...
👤 Generating responses for user 1/20 (a1b2c3d4...)
...
📄 Exported data to checkbox_users_data/
   - Users: checkbox_users_data/checkbox_users.csv
   - Checkbox responses: checkbox_users_data/checkbox_responses.csv
✅ Uploaded users
✅ Uploaded checkbox responses

🎉 Successfully generated and uploaded checkbox users!
📊 Users: 20
☑️ Checkbox responses: 300
📈 Average responses per user: 15.0
📁 CSV files saved in: checkbox_users_data/
```

