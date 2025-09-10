#!/usr/bin/env python3
"""
Working upload script that processes responses in small chunks.
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

def upload_responses_chunked():
    """Upload responses in chunks of 50"""
    print("📤 Uploading single choice responses in chunks...")
    
    # Read all rows first
    responses_file = 'fake_users_data/fake_responses.csv'
    with open(responses_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    
    total = len(rows)
    print(f"📊 Found {total} responses to upload")
    
    # Check how many are already uploaded
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM responses")
    current_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    print(f"📊 Current responses in database: {current_count}")
    
    # Process in chunks of 50
    chunk_size = 50
    uploaded = 0
    
    for chunk_start in range(0, total, chunk_size):
        chunk_end = min(chunk_start + chunk_size, total)
        chunk = rows[chunk_start:chunk_end]
        
        print(f"📦 Processing chunk {chunk_start//chunk_size + 1}/{(total + chunk_size - 1)//chunk_size} (rows {chunk_start + 1}-{chunk_end})")
        
        # Process this chunk
        conn = get_db_connection()
        cursor = conn.cursor()
        
        chunk_uploaded = 0
        for i, row in enumerate(chunk, 1):
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
                
                chunk_uploaded += 1
                
            except Exception as e:
                print(f"   ❌ Error on row {chunk_start + i}: {e}")
                continue
        
        # Commit the chunk
        conn.commit()
        cursor.close()
        conn.close()
        
        uploaded += chunk_uploaded
        print(f"   ✅ Chunk completed. Total uploaded: {uploaded}/{total}")
        
        # Small delay to avoid overwhelming the database
        import time
        time.sleep(0.1)
    
    print(f"✅ Responses upload completed: {uploaded}/{total} responses")

def upload_checkbox_responses_chunked():
    """Upload checkbox responses in chunks of 50"""
    print("📤 Uploading checkbox responses in chunks...")
    
    # Read all rows first
    checkbox_file = 'fake_users_data/fake_checkbox_responses.csv'
    with open(checkbox_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    
    total = len(rows)
    print(f"📊 Found {total} checkbox responses to upload")
    
    # Check how many are already uploaded
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM checkbox_responses")
    current_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    print(f"📊 Current checkbox responses in database: {current_count}")
    
    # Process in chunks of 50
    chunk_size = 50
    uploaded = 0
    
    for chunk_start in range(0, total, chunk_size):
        chunk_end = min(chunk_start + chunk_size, total)
        chunk = rows[chunk_start:chunk_end]
        
        print(f"📦 Processing chunk {chunk_start//chunk_size + 1}/{(total + chunk_size - 1)//chunk_size} (rows {chunk_start + 1}-{chunk_end})")
        
        # Process this chunk
        conn = get_db_connection()
        cursor = conn.cursor()
        
        chunk_uploaded = 0
        for i, row in enumerate(chunk, 1):
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
                
                chunk_uploaded += 1
                
            except Exception as e:
                print(f"   ❌ Error on row {chunk_start + i}: {e}")
                continue
        
        # Commit the chunk
        conn.commit()
        cursor.close()
        conn.close()
        
        uploaded += chunk_uploaded
        print(f"   ✅ Chunk completed. Total uploaded: {uploaded}/{total}")
        
        # Small delay to avoid overwhelming the database
        import time
        time.sleep(0.1)
    
    print(f"✅ Checkbox responses upload completed: {uploaded}/{total} responses")

def main():
    """Main upload function"""
    try:
        print("🚀 Starting chunked responses upload...")
        
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
        
        # Upload responses in chunks
        upload_responses_chunked()
        upload_checkbox_responses_chunked()
        
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
