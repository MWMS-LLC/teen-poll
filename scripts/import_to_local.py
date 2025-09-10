import psycopg2
import csv
from datetime import datetime

def clean_csv_value(value):
    """Clean CSV values and handle multi-line content"""
    if value is None:
        return None
    value = str(value).strip().replace('\ufeff', '')
    if '\n' in value:
        value = value.replace('\n', ' ')
    return value

def import_to_local():
    """Import CSV data into local PostgreSQL database"""
    
    # Local PostgreSQL connection
    DATABASE_URL = "postgresql://postgres@localhost:5432/teen_poll"
    
    conn = None
    try:
        print("🔌 Connecting to local PostgreSQL database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("✅ Connected to local database")
        
        # Clear existing data
        print("🧹 Clearing existing data...")
        cursor.execute("DELETE FROM options")
        cursor.execute("DELETE FROM questions") 
        cursor.execute("DELETE FROM blocks")
        cursor.execute("DELETE FROM categories")
        print("✅ Data cleared")
        
        # Import categories
        print("📁 Importing categories...")
        with open('data/categories.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                day_of_week_str = clean_csv_value(row.get('day_of_week', ''))
                day_of_week_array = None
                if day_of_week_str and day_of_week_str.startswith('{') and day_of_week_str.endswith('}'):
                    content = day_of_week_str[1:-1]
                    day_of_week_array = [int(day.strip()) for day in content.split(',') if day.strip()]
                
                cursor.execute("""
                    INSERT INTO categories (category_name, category_text, day_of_week, day_of_week_text, description, category_text_long, version, uuid, sort_order, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    clean_csv_value(row['category_name']),
                    clean_csv_value(row.get('category_text', '')),
                    day_of_week_array,
                    clean_csv_value(row.get('day_of_week_text', '')),  # New column
                    clean_csv_value(row.get('description', '')),
                    clean_csv_value(row.get('category_text_long', '')),
                    clean_csv_value(row.get('version', '')),
                    clean_csv_value(row.get('uuid', '')),
                    int(row.get('sort_order', 0)),
                    datetime.now()
                ))
        print("✅ Categories imported")
        
        # Import blocks
        print("📁 Importing blocks...")
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
        print("✅ Blocks imported")
        
        # Import questions
        print("📁 Importing questions...")
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
                    int(row.get('max_select', 1)),
                    int(row['block_number']),
                    clean_csv_value(row.get('block_text', '')),
                    row.get('is_start_question', 'false').lower() == 'true',
                    int(row['parent_question_id']) if row.get('parent_question_id') and row.get('parent_question_id').strip() else None,
                    clean_csv_value(row.get('color_code', '')),
                    clean_csv_value(row.get('version', '')),
                    datetime.now()
                ))
        print("✅ Questions imported")
        
        # Import options
        print("📁 Importing options...")
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
        print("✅ Options imported")
        
        conn.commit()
        print("✅ All data imported successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM categories")
        categories_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM blocks")
        blocks_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM questions")
        questions_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM options")
        options_count = cursor.fetchone()[0]
        
        print(f"\n📊 Database Summary:")
        print(f"  Categories: {categories_count}")
        print(f"  Blocks: {blocks_count}")
        print(f"  Questions: {questions_count}")
        print(f"  Options: {options_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import_to_local()

