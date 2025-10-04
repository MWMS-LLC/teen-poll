import psycopg2
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clean_csv_value(value):
    """Clean CSV values and handle multi-line content"""
    if value is None:
        return None
    # Remove BOM and strip whitespace
    value = str(value).strip().replace('\ufeff', '')
    # Handle multi-line content
    if '\n' in value:
        value = value.replace('\n', ' ')
    return value

def import_fake_data():
    """Import fake data into responses and checkbox_responses tables"""
    
    # Database connection
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres@localhost:5432/teen_poll')
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("SUCCESS: Connected to PostgreSQL database")
        
        # Clear existing fake data first
        print("Clearing existing fake data...")
        cursor.execute("DELETE FROM responses WHERE user_uuid IN (SELECT user_uuid FROM users WHERE user_uuid LIKE 'e0fcda19-%' OR user_uuid LIKE '2f6570df-%' OR user_uuid LIKE 'b9925442-%' OR user_uuid LIKE '92374c58-%')")
        cursor.execute("DELETE FROM checkbox_responses WHERE user_uuid IN (SELECT user_uuid FROM users WHERE user_uuid LIKE 'e0fcda19-%' OR user_uuid LIKE '2f6570df-%' OR user_uuid LIKE 'b9925442-%' OR user_uuid LIKE '92374c58-%')")
        cursor.execute("DELETE FROM users WHERE user_uuid LIKE 'e0fcda19-%' OR user_uuid LIKE '2f6570df-%' OR user_uuid LIKE 'b9925442-%' OR user_uuid LIKE '92374c58-%'")
        conn.commit()
        print("SUCCESS: Existing fake data cleared")
        
        # Import fake users first
        print("Importing fake users...")
        with open('data/fake_users_data/fake_users.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                cursor.execute("""
                    INSERT INTO users (user_uuid, year_of_birth, created_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_uuid) DO NOTHING
                """, (
                    clean_csv_value(row['user_uuid']),
                    int(row['year_of_birth']),
                    datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')) if row.get('created_at') else datetime.now()
                ))
                count += 1
        print(f"SUCCESS: {count} fake users imported")
        
        # Import fake responses (single-choice votes)
        print("Importing fake responses...")
        with open('data/fake_users_data/fake_responses.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                cursor.execute("""
                    INSERT INTO responses
                    (user_uuid, question_code, question_text, question_number,
                    category_id, category_name, category_text, block_number,
                    option_id, option_select, option_code, option_text, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    clean_csv_value(row['user_uuid']),
                    clean_csv_value(row['question_code']),
                    clean_csv_value(row['question_text']),
                    int(row['question_number']) if row.get('question_number') and row['question_number'].strip() else None,
                    int(row['category_id']),
                    clean_csv_value(row['category_name']),
                    clean_csv_value(row.get('category_text', '')),
                    int(row['block_number']),
                    int(row['option_id']) if row.get('option_id') and row['option_id'].strip() else None,
                    clean_csv_value(row['option_select']),
                    clean_csv_value(row['option_code']),
                    clean_csv_value(row['option_text']),
                    datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')) if row.get('created_at') else datetime.now()
                ))
                count += 1
        print(f"SUCCESS: {count} fake responses imported")
        
        # Import fake checkbox responses
        print("Importing fake checkbox responses...")
        with open('data/fake_users_data/fake_checkbox_responses.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                cursor.execute("""
                    INSERT INTO checkbox_responses
                    (user_uuid, question_code, question_text, question_number,
                    category_id, category_name, category_text, block_number,
                    option_id, option_select, option_code, option_text,
                    weight, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    clean_csv_value(row['user_uuid']),
                    clean_csv_value(row['question_code']),
                    clean_csv_value(row['question_text']),
                    int(row['question_number']) if row.get('question_number') and row['question_number'].strip() else None,
                    int(row['category_id']),
                    clean_csv_value(row['category_name']),
                    clean_csv_value(row.get('category_text', '')),
                    int(row['block_number']),
                    int(row['option_id']) if row.get('option_id') and row['option_id'].strip() else None,
                    clean_csv_value(row['option_select']),
                    clean_csv_value(row['option_code']),
                    clean_csv_value(row['option_text']),
                    float(row['weight']),
                    datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')) if row.get('created_at') else datetime.now()
                ))
                count += 1
        print(f"SUCCESS: {count} fake checkbox responses imported")
        
        # Commit all data
        conn.commit()
        print("SUCCESS: All fake data imported successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(DISTINCT user_uuid) FROM responses WHERE user_uuid LIKE 'e0fcda19-%'")
        unique_users_responses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT user_uuid) FROM checkbox_responses WHERE user_uuid LIKE 'e0fcda19-%'")
        unique_users_checkbox = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM responses WHERE user_uuid LIKE 'e0fcda19-%'")
        total_responses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM checkbox_responses WHERE user_uuid LIKE 'e0fcda19-%'")
        total_checkbox_responses = cursor.fetchone()[0]
        
        print(f"\nFake Data Summary:")
        print(f"  Unique users (responses): {unique_users_responses}")
        print(f"  Unique users (checkbox): {unique_users_checkbox}")
        print(f"  Total single-choice votes: {total_responses}")
        print(f"  Total checkbox votes: {total_checkbox_responses}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        raise
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    import_fake_data()
