#!/usr/bin/env python3
"""
Upload just a small sample of responses to test the process.
"""

import os
import csv
import pg8000
from urllib.parse import urlparse

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

def upload_sample_responses():
    """Upload just 10 responses as a test"""
    print("🧪 Testing with sample upload (10 responses)...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Read first 10 rows from CSV
    responses_file = 'fake_users_data/fake_responses.csv'
    with open(responses_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        sample_rows = []
        for i, row in enumerate(reader):
            if i >= 10:  # Only take first 10
                break
            sample_rows.append(row)
    
    print(f"📊 Sample data loaded: {len(sample_rows)} rows")
    
    uploaded = 0
    
    for i, row in enumerate(sample_rows, 1):
        print(f"📤 Processing row {i}/10...")
        
        try:
            # Get question_number and option_id from database
            cursor.execute("SELECT question_number FROM questions WHERE question_code = %s", (row['question_code'],))
            question_number_result = cursor.fetchone()
            question_number = question_number_result[0] if question_number_result else None
            
            cursor.execute("SELECT id FROM options WHERE question_code = %s AND option_select = %s", (row['question_code'], row['option_select']))
            option_id_result = cursor.fetchone()
            option_id = option_id_result[0] if option_id_result else None
            
            # Insert the response
            cursor.execute("""
                INSERT INTO responses (
                    user_uuid, question_code, question_text, question_number,
                    category_id, category_name, option_id, option_select,
                    option_code, option_text, block_number, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['user_uuid'], row['question_code'], row['question_text'],
                question_number, int(row['category_id']), row['category_name'],
                option_id, row['option_select'], row['option_code'],
                row['option_text'], int(row['block_number']), row['created_at']
            ))
            
            conn.commit()
            uploaded += 1
            print(f"   ✅ Row {i} uploaded successfully")
            
        except Exception as e:
            print(f"   ❌ Error on row {i}: {e}")
            conn.rollback()
    
    cursor.close()
    conn.close()
    
    print(f"✅ Sample upload completed: {uploaded}/10 responses uploaded")

def main():
    """Main function"""
    print("🚀 Starting sample upload test...")
    
    # Check current status
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM responses")
    current_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    print(f"📊 Current responses in database: {current_count}")
    
    # Upload sample
    upload_sample_responses()
    
    # Check final status
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM responses")
    final_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    print(f"📊 Final responses in database: {final_count}")
    print(f"📈 Added: {final_count - current_count} responses")

if __name__ == "__main__":
    main()
