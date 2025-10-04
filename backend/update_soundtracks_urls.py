#!/usr/bin/env python3
"""
Script to update soundtracks table URLs after moving files from 
myworld-soundtrack/myworld_soundtrack/ to myworld-soundtrack/ (root level)
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def update_soundtracks_urls(database_url, database_name):
    """Update soundtracks table URLs for a specific database"""
    
    print(f"\n=== Updating {database_name} ===")
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print(f"Connected to {database_name}")
        
        # Check current soundtracks table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'soundtracks' 
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print(f"Soundtracks table columns: {[col[0] for col in columns]}")
        
        # Get current soundtracks
        cursor.execute("SELECT song_id, song_title, file_url FROM soundtracks LIMIT 5")
        current_soundtracks = cursor.fetchall()
        print(f"Sample current soundtracks:")
        for row in current_soundtracks:
            print(f"  ID: {row[0]}, Title: {row[1]}, URL: {row[2]}")
        
        # Update URLs - remove the myworld_soundtrack/ prefix
        cursor.execute("""
            UPDATE soundtracks 
            SET file_url = REPLACE(file_url, 'myworld_soundtrack/', '')
            WHERE file_url LIKE '%myworld_soundtrack/%'
        """)
        
        updated_count = cursor.rowcount
        print(f"Updated {updated_count} soundtracks URLs")
        
        # Verify the updates
        cursor.execute("SELECT song_id, song_title, file_url FROM soundtracks LIMIT 5")
        updated_soundtracks = cursor.fetchall()
        print(f"Sample updated soundtracks:")
        for row in updated_soundtracks:
            print(f"  ID: {row[0]}, Title: {row[1]}, URL: {row[2]}")
        
        # Commit changes
        conn.commit()
        print(f"Successfully updated {database_name}")
        
    except Exception as e:
        print(f"Error updating {database_name}: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    """Update soundtracks URLs in both teen and parents databases"""
    
    print("Updating soundtracks URLs after S3 bucket flattening...")
    
    # Get database URLs
    teen_db_url = os.getenv('TEEN_DATABASE_URL')
    parents_db_url = os.getenv('PARENTS_DATABASE_URL')
    
    if not teen_db_url:
        print("TEEN_DATABASE_URL not found in environment variables")
        return
    
    if not parents_db_url:
        print("PARENTS_DATABASE_URL not found in environment variables")
        return
    
    # Update teen database
    update_soundtracks_urls(teen_db_url, "teen_db")
    
    # Update parents database  
    update_soundtracks_urls(parents_db_url, "parents_db")
    
    print("\nAll soundtracks URLs updated successfully!")
    print("\nNext steps:")
    print("1. Rebuild and deploy the schools site")
    print("2. Test the soundtrack page to ensure all songs load correctly")

if __name__ == "__main__":
    main()
