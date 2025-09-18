# main.py
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.db import connection_pool, db_check, db_ssl_status
import logging
logger = logging.getLogger(__name__)

app = FastAPI()

# ------------------ CORS setup ------------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://myworldmysay.com",
    "https://www.myworldmysay.com",
    "https://api.myworldmysay.com",
    "https://teen.myworldmysay.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ DB helper (local to main.py) ------------------
def execute_query(query: str, params: tuple = None, fetch: bool = True):
    """
    Execute a SQL query using the shared connection_pool from backend.db.
    Returns list[dict] when fetch=True, otherwise commits and returns True.
    """
    conn = None
    cursor = None
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            cols = [d[0] for d in cursor.description] if cursor.description else []
            rows = cursor.fetchall() if cursor.description else []
            return [dict(zip(cols, row)) for row in rows]
        else:
            conn.commit()
            return True
    except Exception as e:
        logging.error(f"Database operation failed: {e}")
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail="Database operation failed")
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                connection_pool.putconn(conn)
            except Exception:
                pass

# ------------------ Health ------------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-check")
def get_db_check():
    return {"ok": db_check()}

@app.get("/db-ssl-status")
def get_db_ssl_status():
    return {"ssl": db_ssl_status()}

# ------------------ Categories ------------------
@app.get("/api/categories")
def get_categories():
    query = """
        SELECT *
        FROM categories
        ORDER BY id
    """
    return {"categories": execute_query(query)}

# ------------------ Blocks ------------------
@app.get("/api/categories/{category_id}/blocks")
def get_blocks(category_id: int):
    query = """
        SELECT *
        FROM blocks
        WHERE category_id = %s
        ORDER BY block_number
    """
    return {"blocks": execute_query(query, (category_id,))}

# ------------------ Questions ------------------
@app.get("/api/blocks/{block_code}/questions")
async def get_questions_by_block(block_code: str):
    try:
        # Split "1_1" → category_id=1, block_number=1
        parts = block_code.split('_')
        if len(parts) != 2:
            raise ValueError("Invalid block code format")

        category_id = int(parts[0])
        block_number = int(parts[1])

        query = """
            SELECT *
            FROM questions
            WHERE category_id = %s
              AND block_number = %s
            ORDER BY question_number
        """
        results = execute_query(query, (category_id, block_number))

        # ✅ Wrap like categories/blocks/options
        return {"questions": results}

    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database operation failed: {e}")


# ------------------ Options ------------------
@app.get("/api/questions/{question_code}/options")
def get_options(question_code: str):
    query = """
        SELECT *
        FROM options
        WHERE question_code = %s
        ORDER BY option_select
    """
    return {"options": execute_query(query, (question_code,))}




# ------------------ Soundtracks (stubbed safely) ------------------


@app.get("/api/soundtracks")
def get_soundtracks():
    query = "SELECT * FROM soundtracks ORDER BY id"
    results = execute_query(query)
    return {"soundtracks": results}

@app.get("/api/soundtracks/playlists")
def get_soundtrack_playlists():
    query = "SELECT DISTINCT playlist_tag FROM soundtracks WHERE playlist_tag IS NOT NULL"
    results = execute_query(query)
    playlists = [row["playlist_tag"] for row in results if row.get("playlist_tag")]
    return {"playlists": playlists}



# ------------------ Users ------------------
@app.post("/api/users")
def create_user(user_uuid: str, year_of_birth: int):
    query = """
        INSERT INTO users (user_uuid, year_of_birth)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """
    execute_query(query, (user_uuid, year_of_birth), fetch=False)
    return {"message": "User created or already exists"}

# ------------------ Single-select vote ------------------
@app.post("/api/vote")
def save_vote(
    user_uuid: str,
    question_code: str,
    question_text: str,
    question_number: int,
    category_id: int,
    category_name: str,
    category_text: str,
    option_id: int,
    option_select: str,
    option_code: str,
    option_text: str,
    block_number: int,
    setup_question_code: str = None,
    setup_option_id: int = None
):
    query = """
        INSERT INTO responses (
            user_uuid, question_code, question_text, question_number,
            category_id, category_name, category_text,
            option_id, option_select, option_code, option_text,
            block_number, setup_question_code, setup_option_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    execute_query(query, (
        user_uuid, question_code, question_text, question_number,
        category_id, category_name, category_text,
        option_id, option_select, option_code, option_text,
        block_number, setup_question_code, setup_option_id
    ), fetch=False)
    return {"message": "vote saved"}

# ------------------ Checkbox (multi-select) vote ------------------
@app.post("/api/checkbox_vote")
def save_checkbox_vote(
    user_uuid: str,
    question_code: str,
    question_text: str,
    question_number: int,
    category_id: int,
    category_name: str,
    category_text: str,
    option_id: int,
    option_select: str,
    option_code: str,
    option_text: str,
    block_number: int,
    weight: float,
    setup_question_code: str = None,
    setup_option_id: int = None
):
    query = """
        INSERT INTO checkbox_responses (
            user_uuid, question_code, question_text, question_number,
            category_id, category_name, category_text,
            option_id, option_select, option_code, option_text,
            block_number, weight, setup_question_code, setup_option_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    execute_query(query, (
        user_uuid, question_code, question_text, question_number,
        category_id, category_name, category_text,
        option_id, option_select, option_code, option_text,
        block_number, weight, setup_question_code, setup_option_id
    ), fetch=False)
    return {"message": "checkbox vote saved"}

# ------------------ "Other" text vote ------------------
@app.post("/api/other_vote")
def save_other_vote(
    user_uuid: str,
    question_code: str,
    question_text: str,
    question_number: int,
    category_id: int,
    category_name: str,
    category_text: str,
    block_number: int,
    other_text: str,
    setup_question_code: str = None
):
    query = """
        INSERT INTO other_responses (
            user_uuid, question_code, question_text, question_number,
            category_id, category_name, category_text,
            block_number, other_text, setup_question_code
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    execute_query(query, (
        user_uuid, question_code, question_text, question_number,
        category_id, category_name, category_text,
        block_number, other_text, setup_question_code
    ), fetch=False)
    return {"message": "other vote saved"}


# ------------------ Age Validation ------------------
from datetime import datetime

@app.post("/api/validate-age")
def validate_age(payload: dict):
    try:
        year_of_birth = payload.get("year_of_birth")

        if not year_of_birth or not str(year_of_birth).isdigit():
            raise HTTPException(status_code=400, detail="Invalid year of birth")

        yob = int(year_of_birth)
        current_year = datetime.now().year
        age = current_year - yob

        if age < 13:
            return {"valid": False, "reason": "too_young"}
        elif age > 120:
            return {"valid": False, "reason": "invalid_year"}
        else:
            return {"valid": True, "age": age}

    except Exception as e:
        logger.error(f"Age validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Age validation failed: {e}")


# ------------------ Playlists ------------------
@app.get("/api/playlists")
def get_playlists():
    query = "SELECT * FROM playlists ORDER BY id"
    results = execute_query(query)
    return {"playlists": results}


@app.get("/api/playlists/{playlist_id}")
def get_playlist(playlist_id: int):
    query = "SELECT * FROM playlists WHERE id = %s"
    results = execute_query(query, (playlist_id,))
    if not results:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return {"playlist": results[0]}


@app.get("/api/playlists/{playlist_id}/songs")
def get_playlist_songs(playlist_id: int):
    query = """
        SELECT ps.*, s.*
        FROM playlist_songs ps
        JOIN soundtracks s ON ps.song_id = s.id
        WHERE ps.playlist_id = %s
        ORDER BY ps.order_number
    """
    results = execute_query(query, (playlist_id,))
    return {"songs": results}
