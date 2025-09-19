# run in root/backend: cd backend
import os
import csv
from db import get_db_connection

# Always resolve path relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "soundtracks.csv")

def import_soundtracks(csv_file=CSV_PATH):
    with get_db_connection() as conn:
        cur = conn.cursor()
        with open(csv_file, newline='', encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            
            # Normalize headers (strip spaces, lowercase)
            reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
            print("Detected headers:", reader.fieldnames)

            for row in reader:
                # Normalize row keys the same way
                norm = {k.strip().lower(): (v.strip() if v else None) for k, v in row.items()}

                playlist_tag = norm["playlist_tag"].replace("_", " ") if norm.get("playlist_tag") else None

                cur.execute("""
                    INSERT INTO soundtracks 
                        (song_id, song_title, mood_tag, playlist_tag, lyrics_snippet, featured, featured_order, file_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (song_id) DO UPDATE SET
                        song_title = EXCLUDED.song_title,
                        mood_tag = EXCLUDED.mood_tag,
                        playlist_tag = EXCLUDED.playlist_tag,
                        lyrics_snippet = EXCLUDED.lyrics_snippet,
                        featured = EXCLUDED.featured,
                        featured_order = EXCLUDED.featured_order,
                        file_url = EXCLUDED.file_url;
                """, (
                    norm.get("song_id"),
                    norm.get("song_title"),
                    norm.get("mood_tag"),
                    playlist_tag,
                    norm.get("lyrics_snippet"),
                    str(norm.get("featured")).lower() in ("true", "1", "yes"),
                    int(norm["featured_order"]) if norm.get("featured_order") else None,
                    norm.get("file_url"),
                ))

        conn.commit()
        print(f"✅ Soundtracks imported successfully from {csv_file}")

if __name__ == "__main__":
    import_soundtracks()
