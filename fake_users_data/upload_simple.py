#!/usr/bin/env python3
"""
Very simple upload script - one row at a time with immediate commits.
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

def upload_responses_simple():
    """Upload responses one by one"""
    print("📤 Uploading single choice responses...")
    
    # Read all rows first
    responses_file = 'fake_users_data/fake_responses.csv'
    with open(responses_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    
    total = len(rows)
    print(f"📊 Found {total} responses to upload")
    
    uploaded = 0
    
    for i, row in enumerate(rows, 1):
        # Create new connection for each row to avoid timeout issues
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
            
            if i % 100 == 0 or i == total:
                print(f"   ✅ Progress: {i}/{total} responses uploaded")
            
        except Exception as e:
            print(f"   ❌ Error on row {i}: {e}")
            conn.rollback()
        
        finally:
            cursor.close()
            conn.close()
    
    print(f"✅ Responses upload completed: {uploaded}/{total} responses")

def upload_checkbox_responses_simple():
    """Upload checkbox responses one by one"""
    print("📤 Uploading checkbox responses...")
    
    # Read all rows first
    checkbox_file = 'fake_users_data/fake_checkbox_responses.csv'
    with open(checkbox_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    
    total = len(rows)
    print(f"📊 Found {total} checkbox responses to upload")
    
    uploaded = 0
    
    for i, row in enumerate(rows, 1):
        # Create new connection for each row to avoid timeout issues
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get question_number and option_id from database
            cursor.execute("SELECT question_number FROM questions WHERE question_code = %s", (row['question_code'],))
            question_number_result = cursor.fetchone()
            question_number = question_number_result[0] if question_number_result else None
            
            cursor.execute("SELECT id FROM options WHERE question_code = %s AND option_select = %s", (row['question_code'], row['option_select']))
            option_id_result = cursor.fetchone()
            option_id = option_id_result[0] if option_id_result else None
            
            # Insert the checkbox response
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
            
            conn.commit()
            uploaded += 1
            
            if i % 100 == 0 or i == total:
                print(f"   ✅ Progress: {i}/{total} checkbox responses uploaded")
            
        except Exception as e:
            print(f"   ❌ Error on row {i}: {e}")
            conn.rollback()
        
        finally:
            cursor.close()
            conn.close()
    
    print(f"✅ Checkbox responses upload completed: {uploaded}/{total} responses")

def main():
    """Main upload function"""
    try:
        print("🚀 Starting simple responses upload...")
        
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
        
        # Upload responses
        upload_responses_simple()
        upload_checkbox_responses_simple()
        
        # Final status check
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM responses")
        final_responses = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM checkbox_responses")
        final_checkbox = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print("\n🎉 Upload completed successfully!")
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
