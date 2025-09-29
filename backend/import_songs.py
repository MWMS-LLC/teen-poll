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

        # --- Clear old data ---
        print("🧹 Truncating soundtracks table...")
        cur.execute("TRUNCATE TABLE soundtracks RESTART IDENTITY CASCADE;")
        conn.commit()
        print("✅ Soundtracks table truncated")

        with open(csv_file, newline='', encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            # Normalize headers (strip spaces, lowercase)
            reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
            print("Detected headers:", reader.fieldnames)

            for row in reader:
                norm = {k.strip().lower(): (v.strip() if v else None) for k, v in row.items()}

                cur.execute("""
                    INSERT INTO soundtracks 
                        (song_id, song_title, mood_tag, playlist_tag, lyrics_snippet, featured, featured_order, file_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    norm.get("song_id"),
                    norm.get("song_title"),
                    norm.get("mood_tag"),
                    norm.get("playlist_tag"),   # take CSV as-is, no "_" replacement
                    norm.get("lyrics_snippet"),
                    str(norm.get("featured")).lower() in ("true", "1", "yes"),
                    int(norm["featured_order"]) if norm.get("featured_order") else None,
                    norm.get("file_url"),
                ))

        conn.commit()
        print(f"✅ Soundtracks imported successfully from {csv_file}")

        # --- Summary ---
        cur.execute("SELECT COUNT(*) FROM soundtracks")
        print(f"  Soundtracks: {cur.fetchone()[0]}")

if __name__ == "__main__":
    import_soundtracks()
