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

def import_render_batch():
    """Import CSV data to Render in small batches"""
    
    DATABASE_URL = "postgresql://mwms_polls_db_rbj5_user:jhNQweOFPAm9jm3GwQgqIduXBvWsrlbe@dpg-d2aes03e5dus73cpe30g-a.oregon-postgres.render.com/mwms_polls_db_rbj5"
    
    conn = None
    try:
        print("🔌 Connecting to Render...")
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
        cursor = conn.cursor()
        print("✅ Connected")
        
        # Clear data in small batches
        print("🧹 Clearing data...")
        cursor.execute("DELETE FROM options LIMIT 1000")
        cursor.execute("DELETE FROM questions LIMIT 1000") 
        cursor.execute("DELETE FROM blocks LIMIT 1000")
        cursor.execute("DELETE FROM categories LIMIT 1000")
        conn.commit()
        print("✅ Data cleared")
        
        # Import categories (small file, should work)
        print("📁 Importing categories...")
        with open('data/categories.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
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
                    clean_csv_value(row.get('day_of_week_text', '')),
                    clean_csv_value(row.get('description', '')),
                    clean_csv_value(row.get('category_text_long', '')),
                    clean_csv_value(row.get('version', '')),
                    clean_csv_value(row.get('uuid', '')),
                    int(row.get('sort_order', 0)),
                    datetime.now()
                ))
                count += 1
                if count % 5 == 0:
                    print(f"  ... {count} categories")
                    conn.commit()  # Commit every 5 rows
        
        conn.commit()
        print(f"✅ Categories imported: {count} rows")
        
        # Test if we can continue
        print("📊 Testing connection...")
        cursor.execute("SELECT COUNT(*) FROM categories")
        count = cursor.fetchone()[0]
        print(f"✅ Categories in database: {count}")
        
        print("🎉 Batch import successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import_render_batch()

