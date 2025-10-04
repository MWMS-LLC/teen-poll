#!/usr/bin/env python3
"""
Script to export soundtracks from database to CSV with updated URLs
"""

import psycopg2
import csv
import os
from dotenv import load_dotenv

load_dotenv()

def export_soundtracks_csv(database_url, output_file):
    """Export soundtracks from database to CSV file"""
    
    print(f"Exporting soundtracks to {output_file}...")
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("Connected to database")
        
        # Get all soundtracks
        cursor.execute("""
            SELECT song_id, song_title, mood_tag, playlist_tag, lyrics_snippet, 
                   featured, featured_order, file_url, created_at
            FROM soundtracks 
            ORDER BY featured_order, song_id
        """)
        
        soundtracks = cursor.fetchall()
        print(f"Found {len(soundtracks)} soundtracks")
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'song_id', 'song_title', 'mood_tag', 'playlist_tag', 
                'lyrics_snippet', 'featured', 'featured_order', 'file_url'
            ])
            
            # Write data
            for row in soundtracks:
                writer.writerow([
                    row[0],  # song_id
                    row[1],  # song_title
                    row[2],  # mood_tag
                    row[3],  # playlist_tag
                    row[4],  # lyrics_snippet
                    row[5],  # featured
                    row[6],  # featured_order
                    row[7]   # file_url (already updated in database)
                ])
        
        print(f"Successfully exported {len(soundtracks)} soundtracks to {output_file}")
        
        # Show sample of exported data
        print("\nSample exported soundtracks:")
        for i, row in enumerate(soundtracks[:3]):
            print(f"  {i+1}. {row[1]} - {row[7]}")
        
    except Exception as e:
        print(f"Error exporting soundtracks: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    """Export soundtracks from teen database to schools CSV"""
    
    print("Exporting updated soundtracks to schools CSV...")
    
    # Get database URL
    teen_db_url = os.getenv('TEEN_DATABASE_URL')
    if not teen_db_url:
        print("TEEN_DATABASE_URL not found in environment variables")
        return
    
    # Export to schools CSV
    output_file = r"C:\Users\MWMS\schools1002\frontend\public\soundtracks.csv"
    export_soundtracks_csv(teen_db_url, output_file)
    
    print(f"\nSchools CSV updated at: {output_file}")
    print("Next steps:")
    print("1. Rebuild schools frontend")
    print("2. Upload to S3")

if __name__ == "__main__":
    main()




