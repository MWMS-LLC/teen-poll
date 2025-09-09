#!/usr/bin/env python3
"""
Simple script to upload fake users from CSV files to the database with progress tracking.
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

def upload_users(conn):
    """Upload users from CSV"""
    cursor = conn.cursor()
    
    print("📤 Uploading users...")
    users_file = 'fake_users_data/fake_users.csv'
    
    with open(users_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        total = len(rows)
        
        for i, row in enumerate(rows, 1):
            cursor.execute("""
                INSERT INTO users (user_uuid, year_of_birth, created_at)
                VALUES (%s, %s, %s)
            """, (row['user_uuid'], int(row['year_of_birth']), row['created_at']))
            
            if i % 5 == 0 or i == total:
                print(f"   Users: {i}/{total} uploaded")
    
    conn.commit()
    cursor.close()
    print(f"✅ Users upload completed: {total} users")

def upload_responses(conn):
    """Upload single choice responses from CSV"""
    cursor = conn.cursor()
    
    print("📤 Uploading single choice responses...")
    responses_file = 'fake_users_data/fake_responses.csv'
    
    with open(responses_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        total = len(rows)
        
        for i, row in enumerate(rows, 1):
            # Get question_number and option_id from database
            cursor.execute("SELECT question_number FROM questions WHERE question_code = %s", (row['question_code'],))
            question_number_result = cursor.fetchone()
            question_number = question_number_result[0] if question_number_result else None
            
            cursor.execute("SELECT id FROM options WHERE question_code = %s AND option_select = %s", (row['question_code'], row['option_select']))
            option_id_result = cursor.fetchone()
            option_id = option_id_result[0] if option_id_result else None
            
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
            
            if i % 1000 == 0 or i == total:
                print(f"   Responses: {i}/{total} uploaded")
    
    conn.commit()
    cursor.close()
    print(f"✅ Responses upload completed: {total} responses")

def upload_checkbox_responses(conn):
    """Upload checkbox responses from CSV"""
    cursor = conn.cursor()
    
    print("📤 Uploading checkbox responses...")
    checkbox_file = 'fake_users_data/fake_checkbox_responses.csv'
    
    with open(checkbox_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        total = len(rows)
        
        for i, row in enumerate(rows, 1):
            # Get question_number and option_id from database
            cursor.execute("SELECT question_number FROM questions WHERE question_code = %s", (row['question_code'],))
            question_number_result = cursor.fetchone()
            question_number = question_number_result[0] if question_number_result else None
            
            cursor.execute("SELECT id FROM options WHERE question_code = %s AND option_select = %s", (row['question_code'], row['option_select']))
            option_id_result = cursor.fetchone()
            option_id = option_id_result[0] if option_id_result else None
            
            cursor.execute("""
                INSERT INTO checkbox_responses (
                    user_uuid, question_code, question_text, question_number,
                    category_id, category_name, option_id, option_select,
                    option_code, option_text, block_number, weight, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['user_uuid'], row['question_code'], row['question_text'],
                question_number, int(row['category_id']), row['category_name'],
                option_id, row['option_select'], row['option_code'],
                row['option_text'], int(row['block_number']), float(row['weight']), 
                row['created_at']
            ))
            
            if i % 1000 == 0 or i == total:
                print(f"   Checkbox responses: {i}/{total} uploaded")
    
    conn.commit()
    cursor.close()
    print(f"✅ Checkbox responses upload completed: {total} responses")

def main():
    """Main upload function"""
    try:
        print("🚀 Starting fake users upload to database...")
        
        # Connect to database
        conn = get_db_connection()
        print("✅ Connected to database")
        
        # Upload users first (you should see these appear in DBeaver)
        upload_users(conn)
        
        # Check current status
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.close()
        print(f"📊 Current users in database: {user_count}")
        
        # Upload responses
        upload_responses(conn)
        upload_checkbox_responses(conn)
        
        # Final status check
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        final_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM responses")
        final_responses = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM checkbox_responses")
        final_checkbox = cursor.fetchone()[0]
        cursor.close()
        
        print("\n🎉 Upload completed successfully!")
        print(f"📊 Final database status:")
        print(f"   Users: {final_users}")
        print(f"   Responses: {final_responses}")
        print(f"   Checkbox responses: {final_checkbox}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
