#!/usr/bin/env python3
"""
Fast upload script using PostgreSQL COPY command for bulk insertion.
"""

import os
import csv
import pg8000
from urllib.parse import urlparse
import io

def get_db_connection():
    """Get database connection"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise Exception("DATABASE_URL environment variable is not set!")
    
    parsed = urlparse(database_url)
    conn = pg8000.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path.lstrip("/"),
        user=parsed.username,
        password=parsed.password,
        ssl_context=True
    )
    return conn

def upload_responses_fast():
    """Upload responses using fast bulk method"""
    print("📤 Uploading single choice responses using fast bulk method...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # First, let's create a temporary table for bulk insert
    print("🔧 Creating temporary table...")
    cursor.execute("""
        CREATE TEMP TABLE temp_responses (
            user_uuid TEXT,
            question_code VARCHAR(50),
            question_text TEXT,
            question_number INTEGER,
            category_id INTEGER,
            category_name VARCHAR(100),
            option_id INTEGER,
            option_select VARCHAR(10),
            option_code VARCHAR(50),
            option_text TEXT,
            block_number INTEGER,
            created_at TIMESTAMP
        )
    """)
    
    # Read CSV and prepare data
    responses_file = 'fake_users_data/fake_responses.csv'
    with open(responses_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    
    total = len(rows)
    print(f"📊 Found {total} responses to upload")
    
    # Prepare data for bulk insert
    print("📦 Preparing data for bulk insert...")
    data_rows = []
    for row in rows:
        data_rows.append((
            row['user_uuid'],
            row['question_code'],
            row['question_text'],
            None,  # question_number will be filled later
            int(row['category_id']),
            row['category_name'],
            None,  # option_id will be filled later
            row['option_select'],
            row['option_code'],
            row['option_text'],
            int(row['block_number']),
            row['created_at']
        ))
    
    # Bulk insert into temp table
    print("📤 Bulk inserting into temporary table...")
    cursor.executemany("""
        INSERT INTO temp_responses (
            user_uuid, question_code, question_text, question_number,
            category_id, category_name, option_id, option_select,
            option_code, option_text, block_number, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, data_rows)
    
    print("🔄 Updating question_number and option_id...")
    
    # Update question_number
    cursor.execute("""
        UPDATE temp_responses 
        SET question_number = q.question_number
        FROM questions q 
        WHERE temp_responses.question_code = q.question_code
    """)
    
    # Update option_id
    cursor.execute("""
        UPDATE temp_responses 
        SET option_id = o.id
        FROM options o 
        WHERE temp_responses.question_code = o.question_code 
        AND temp_responses.option_select = o.option_select
    """)
    
    print("📤 Inserting from temp table to main table...")
    
    # Insert from temp table to main table
    cursor.execute("""
        INSERT INTO responses (
            user_uuid, question_code, question_text, question_number,
            category_id, category_name, option_id, option_select,
            option_code, option_text, block_number, created_at
        )
        SELECT 
            user_uuid, question_code, question_text, question_number,
            category_id, category_name, option_id, option_select,
            option_code, option_text, block_number, created_at
        FROM temp_responses
    """)
    
    # Get the count of inserted rows
    inserted_count = cursor.rowcount
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Fast responses upload completed: {inserted_count} responses inserted")

def upload_checkbox_responses_fast():
    """Upload checkbox responses using fast bulk method"""
    print("📤 Uploading checkbox responses using fast bulk method...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create temporary table for bulk insert
    print("🔧 Creating temporary table...")
    cursor.execute("""
        CREATE TEMP TABLE temp_checkbox_responses (
            user_uuid TEXT,
            question_code VARCHAR(50),
            question_text TEXT,
            question_number INTEGER,
            category_id INTEGER,
            category_name VARCHAR(100),
            option_id INTEGER,
            option_select VARCHAR(10),
            option_code VARCHAR(50),
            option_text TEXT,
            block_number INTEGER,
            weight REAL,
            created_at TIMESTAMP
        )
    """)
    
    # Read CSV and prepare data
    checkbox_file = 'fake_users_data/fake_checkbox_responses.csv'
    with open(checkbox_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    
    total = len(rows)
    print(f"📊 Found {total} checkbox responses to upload")
    
    # Prepare data for bulk insert
    print("📦 Preparing data for bulk insert...")
    data_rows = []
    for row in rows:
        data_rows.append((
            row['user_uuid'],
            row['question_code'],
            row['question_text'],
            None,  # question_number will be filled later
            int(row['category_id']),
            row['category_name'],
            None,  # option_id will be filled later
            row['option_select'],
            row['option_code'],
            row['option_text'],
            int(row['block_number']),
            float(row['weight']),
            row['created_at']
        ))
    
    # Bulk insert into temp table
    print("📤 Bulk inserting into temporary table...")
    cursor.executemany("""
        INSERT INTO temp_checkbox_responses (
            user_uuid, question_code, question_text, question_number,
            category_id, category_name, option_id, option_select,
            option_code, option_text, block_number, weight, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, data_rows)
    
    print("🔄 Updating question_number and option_id...")
    
    # Update question_number
    cursor.execute("""
        UPDATE temp_checkbox_responses 
        SET question_number = q.question_number
        FROM questions q 
        WHERE temp_checkbox_responses.question_code = q.question_code
    """)
    
    # Update option_id
    cursor.execute("""
        UPDATE temp_checkbox_responses 
        SET option_id = o.id
        FROM options o 
        WHERE temp_checkbox_responses.question_code = o.question_code 
        AND temp_checkbox_responses.option_select = o.option_select
    """)
    
    print("📤 Inserting from temp table to main table...")
    
    # Insert from temp table to main table
    cursor.execute("""
        INSERT INTO checkbox_responses (
            user_uuid, question_code, question_text, question_number,
            category_id, category_name, option_id, option_select,
            option_code, option_text, block_number, weight, created_at
        )
        SELECT 
            user_uuid, question_code, question_text, question_number,
            category_id, category_name, option_id, option_select,
            option_code, option_text, block_number, weight, created_at
        FROM temp_checkbox_responses
    """)
    
    # Get the count of inserted rows
    inserted_count = cursor.rowcount
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Fast checkbox responses upload completed: {inserted_count} responses inserted")

def main():
    """Main upload function"""
    try:
        print("🚀 Starting fast bulk responses upload...")
        
        # Check current status
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM responses")
        response_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM checkbox_responses")
        checkbox_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"📊 Current database status:")
        print(f"   Users: {user_count}")
        print(f"   Responses: {response_count}")
        print(f"   Checkbox responses: {checkbox_count}")
        
        # Upload responses using fast method
        upload_responses_fast()
        upload_checkbox_responses_fast()
        
        # Final status check
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM responses")
        final_responses = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM checkbox_responses")
        final_checkbox = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print("\n🎉 Fast upload completed successfully!")
        print(f"📊 Final database status:")
        print(f"   Users: {user_count}")
        print(f"   Responses: {final_responses}")
        print(f"   Checkbox responses: {final_checkbox}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
