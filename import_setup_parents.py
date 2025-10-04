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

def import_setup_data_parents():
    """Import CSV data into PostgreSQL database for parents version"""
    
    # Database connection - use parents database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:NBem0YTOfN94yKqFSw5F@mwms-instance.c320aqgmywbc.us-east-2.rds.amazonaws.com:5432/parents_db?sslmode=require')
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("SUCCESS: Connected to PostgreSQL parents database")
        
        # Read and execute fresh schema
        print("Setting up fresh database schema for parents...")
        
        # Execute setup schema
        with open('schema_setup.sql', 'r') as f:
            setup_schema = f.read()
        cursor.execute(setup_schema)
        print("SUCCESS: Parents setup schema created")

        # Clear old data before inserting new
        cursor.execute("TRUNCATE TABLE options RESTART IDENTITY CASCADE;")
        cursor.execute("TRUNCATE TABLE questions RESTART IDENTITY CASCADE;")
        cursor.execute("TRUNCATE TABLE blocks RESTART IDENTITY CASCADE;")
        cursor.execute("TRUNCATE TABLE categories RESTART IDENTITY CASCADE;")
        conn.commit()
        print("SUCCESS: Existing parents setup data truncated")

        
        # Final commit after truncation
        conn.commit()

        
        # Import CSV data
        print("Importing CSV data for parents...")
        
        # Import categories
        print("  Importing categories...")
        with open('data/categories.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse day_of_week array from PostgreSQL format "{0,1,2,3,4,5,6}"
                day_of_week_str = clean_csv_value(row.get('day_of_week', ''))
                day_of_week_array = None
                if day_of_week_str and day_of_week_str.startswith('{') and day_of_week_str.endswith('}'):
                    content = day_of_week_str[1:-1]  # Remove { and }
                    day_of_week_array = [int(day.strip()) for day in content.split(',') if day.strip()]
                
                cursor.execute("""
                    INSERT INTO categories (category_name, category_text, day_of_week, description, category_text_long, version, uuid, sort_order, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    clean_csv_value(row['category_name']),
                    clean_csv_value(row.get('category_text', '')),
                    day_of_week_array,
                    clean_csv_value(row.get('description', '')),
                    clean_csv_value(row.get('category_text_long', '')),
                    clean_csv_value(row.get('version', '')),
                    clean_csv_value(row.get('uuid', '')),
                    int(row.get('sort_order', 0)),
                    datetime.now()
                ))
        print(f"    SUCCESS: Categories imported for parents")
        
        # Import blocks
        print("  Importing blocks...")
        with open('data/blocks.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                    INSERT INTO blocks (category_id, block_number, block_code, block_text, version, uuid, category_name, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    int(row['category_id']),
                    int(row['block_number']),
                    clean_csv_value(row['block_code']),
                    clean_csv_value(row['block_text']),
                    clean_csv_value(row.get('version', '')),
                    clean_csv_value(row.get('uuid', '')),
                    clean_csv_value(row.get('category_name', '')),
                    datetime.now()
                ))
        print(f"    SUCCESS: Blocks imported for parents")
        
        # Import questions
        print("  Importing questions...")
        with open('data/questions.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                    INSERT INTO questions (category_id, question_code, question_number, question_text, check_box, max_select, block_number, block_text, is_start_question, parent_question_id, color_code, version, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    int(row['category_id']),
                    clean_csv_value(row['question_code']),
                    int(row['question_number']),
                    clean_csv_value(row['question_text']),
                    row.get('check_box', 'false').lower() == 'true',
                    int(row.get('max_select', 10)) if row.get('max_select') and row.get('max_select').strip() and row.get('max_select') != '' else (10 if row.get('check_box', 'false').lower() == 'true' else 1),
                    int(row['block_number']),
                    clean_csv_value(row.get('block_text', '')),
                    row.get('is_start_question', 'false').lower() == 'true',
                    int(row['parent_question_id']) if row.get('parent_question_id') and row.get('parent_question_id').strip() else None,
                    clean_csv_value(row.get('color_code', '')),
                    clean_csv_value(row.get('version', '')),
                    datetime.now()
                ))
        print(f"    SUCCESS: Questions imported for parents")
        
        # Import options
        print("  Importing options...")
        with open('data/options.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                    INSERT INTO options (category_id, question_code, question_number, question_text, check_box, block_number, block_text, option_select, option_code, option_text, response_message, companion_advice, tone_tag, next_question_id, version, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    int(row['category_id']),
                    clean_csv_value(row['question_code']),
                    int(row['question_number']),
                    clean_csv_value(row['question_text']),
                    row.get('check_box', 'false').lower() == 'true',
                    int(row['block_number']),
                    clean_csv_value(row['block_text']),
                    clean_csv_value(row['option_select']),
                    clean_csv_value(row['option_code']),
                    clean_csv_value(row['option_text']),
                    clean_csv_value(row.get('response_message', '')),
                    clean_csv_value(row.get('companion_advice', '')),
                    clean_csv_value(row.get('tone_tag', '')),
                    int(row['next_question_id']) if row.get('next_question_id') and row.get('next_question_id').strip() else None,
                    clean_csv_value(row.get('version', '')),
                    datetime.now()
                ))
        print(f"    SUCCESS: Options imported for parents")
        
        # Commit all data
        conn.commit()
        print("SUCCESS: All parents data imported successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM categories")
        categories_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM blocks")
        blocks_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM questions")
        questions_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM options")
        options_count = cursor.fetchone()[0]
        
        print(f"\nParents Database Summary:")
        print(f"  Categories: {categories_count}")
        print(f"  Blocks: {blocks_count}")
        print(f"  Questions: {questions_count}")
        print(f"  Options: {options_count}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        raise
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    import_setup_data_parents()




