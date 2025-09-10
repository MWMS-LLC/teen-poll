import psycopg2

def add_column():
    """Just add the day_of_week_text column"""
    
    DATABASE_URL = "postgresql://mwms_polls_db_rbj5_user:jhNQweOFPAm9jm3GwQgqIduXBvWsrlbe@dpg-d2aes03e5dus73cpe30g-a.oregon-postgres.render.com/mwms_polls_db_rbj5"
    
    try:
        print("Adding day_of_week_text column...")
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=5)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'categories' 
            AND column_name = 'day_of_week_text'
        """)
        
        if cursor.fetchone():
            print("Column already exists")
        else:
            cursor.execute("ALTER TABLE categories ADD COLUMN day_of_week_text TEXT")
            print("Column added successfully")
        
        conn.commit()
        conn.close()
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_column()

