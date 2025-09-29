# main.py
# main.py (updated: unified /api/vote handler that uses responses, checkbox_responses, other_responses)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.db import connection_pool, db_check, db_ssl_status
from pydantic import BaseModel
from typing import List, Optional, Union
import logging
from datetime import datetime, timezone
import zlib

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




# ------------------ Separate vote handler (single, checkbox, other) ------------------
class VoteIn(BaseModel):
    user_uuid: str
    question_code: str
    option_id: Optional[int] = None
    other_text: Optional[str] = None
    option_select: Optional[str] = None   # e.g. "A", "B"
    is_checkbox: Optional[bool] = False
    option_ids: Optional[List[int]] = None
    vote_weight: Optional[float] = 1.0

def _lock_key_for(user_uuid: str, question_code: str) -> int:
    return zlib.crc32(f"{user_uuid}|{question_code}".encode("utf-8"))

def _get_other_responses_columns():
    rows = execute_query("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'other_responses'
    """)
    return {r["column_name"] for r in rows} if rows else set()

def _fetch_option_meta(conn_or_run, option_id):
    rows = execute_query(
        "SELECT id, option_select, option_code, option_text FROM options WHERE id = %s",
        (option_id,)
    )
    return rows[0] if rows else None

def _fetch_question_meta(conn_or_run, question_code):
    rows = execute_query(
        "SELECT question_text, question_number, category_id, block_number FROM questions WHERE question_code = %s LIMIT 1",
        (question_code,)
    )
    return rows[0] if rows else None

def _fetch_category_meta_by_id(conn_or_run, category_id):
    rows = execute_query(
        "SELECT category_name, category_text FROM categories WHERE id = %s LIMIT 1",
        (category_id,)
    )
    return rows[0] if rows else {"category_name": None, "category_text": None}

@app.post("/api/vote")
def save_vote(payload: VoteIn):
    """
    Save a vote (single choice, checkbox, or other text).
    Keeps history by inserting new rows instead of overwriting.
    Returns tallies per option.
    """
    user_uuid = payload.user_uuid
    qcode = payload.question_code
    now = datetime.now(timezone.utc)
    vw = float(payload.vote_weight or 1.0)

    if not user_uuid or not qcode:
        raise HTTPException(status_code=422, detail="user_uuid and question_code required")

    # ---------- CHECKBOX MODE ----------
    if payload.is_checkbox:
        if not payload.option_ids or not isinstance(payload.option_ids, list):
            raise HTTPException(status_code=422, detail="option_ids (list) required for checkbox votes")

        qmeta = _fetch_question_meta(None, qcode) or {}
        catmeta = _fetch_category_meta_by_id(None, qmeta.get("category_id"))

        insert_sql = """
        INSERT INTO checkbox_responses
          (user_uuid, question_code, question_text, question_number, category_id, category_name,
           category_text, option_id, option_select, option_code, option_text, block_number,
           created_at, vote_weight)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        for opt_id in payload.option_ids:
            opt_meta = _fetch_option_meta(None, opt_id)
            if not opt_meta:
                raise HTTPException(status_code=422, detail=f"option id {opt_id} not found")
            execute_query(insert_sql, (
                user_uuid, qcode,
                qmeta.get("question_text"), qmeta.get("question_number"), qmeta.get("category_id"),
                catmeta.get("category_name"), catmeta.get("category_text"),
                opt_meta["id"], opt_meta["option_select"], opt_meta["option_code"], opt_meta["option_text"],
                qmeta.get("block_number"),
                now, vw
            ), fetch=False)

        if payload.other_text and payload.other_text.strip():
            other_cols = _get_other_responses_columns()
            insert_cols, insert_vals = [], []
            if "user_uuid" in other_cols: insert_cols.append("user_uuid"); insert_vals.append(user_uuid)
            if "question_code" in other_cols: insert_cols.append("question_code"); insert_vals.append(qcode)
            if "other_text" in other_cols: insert_cols.append("other_text"); insert_vals.append(payload.other_text.strip())
            if "created_at" in other_cols: insert_cols.append("created_at"); insert_vals.append(now)
            if "vote_weight" in other_cols: insert_cols.append("vote_weight"); insert_vals.append(vw)
            cols_sql = ",".join(insert_cols)
            placeholders = ",".join(["%s"] * len(insert_vals))
            execute_query(f"INSERT INTO other_responses ({cols_sql}) VALUES ({placeholders})", tuple(insert_vals), fetch=False)

    # ---------- SINGLE CHOICE MODE ----------
    else:
        is_other = (payload.option_id is None) and (payload.other_text and payload.other_text.strip())
        qmeta = _fetch_question_meta(None, qcode) or {}
        catmeta = _fetch_category_meta_by_id(None, qmeta.get("category_id"))

        if is_other:
            other_text = payload.other_text.strip()
            execute_query("""
                INSERT INTO responses
                  (user_uuid, question_code, question_text, question_number, category_id, category_name, category_text,
                   option_id, option_select, option_code, option_text, block_number, created_at, vote_weight)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                user_uuid, qcode,
                qmeta.get("question_text"), qmeta.get("question_number"), qmeta.get("category_id"),
                catmeta.get("category_name"), catmeta.get("category_text"),
                None, "Other", "OTHER", other_text[:500],
                qmeta.get("block_number"),
                now, vw
            ), fetch=False)

            other_cols = _get_other_responses_columns()
            insert_cols, insert_vals = [], []
            if "user_uuid" in other_cols: insert_cols.append("user_uuid"); insert_vals.append(user_uuid)
            if "question_code" in other_cols: insert_cols.append("question_code"); insert_vals.append(qcode)
            if "other_text" in other_cols: insert_cols.append("other_text"); insert_vals.append(other_text)
            if "created_at" in other_cols: insert_cols.append("created_at"); insert_vals.append(now)
            if "vote_weight" in other_cols: insert_cols.append("vote_weight"); insert_vals.append(vw)
            cols_sql = ",".join(insert_cols)
            placeholders = ",".join(["%s"] * len(insert_vals))
            execute_query(f"INSERT INTO other_responses ({cols_sql}) VALUES ({placeholders})", tuple(insert_vals), fetch=False)

        else:
            opt_meta = _fetch_option_meta(None, payload.option_id)
            if not opt_meta:
                raise HTTPException(status_code=422, detail=f"option id {payload.option_id} not found")
            execute_query("""
                INSERT INTO responses
                  (user_uuid, question_code, question_text, question_number, category_id, category_name, category_text,
                   option_id, option_select, option_code, option_text, block_number, created_at, vote_weight)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                user_uuid, qcode,
                qmeta.get("question_text"), qmeta.get("question_number"), qmeta.get("category_id"),
                catmeta.get("category_name"), catmeta.get("category_text"),
                opt_meta["id"], opt_meta["option_select"], opt_meta["option_code"], opt_meta["option_text"],
                qmeta.get("block_number"),
                now, vw
            ), fetch=False)

    # ---------- AGGREGATES ----------
    option_rows = execute_query(
        "SELECT id, option_code FROM options WHERE question_code = %s ORDER BY id",
        (qcode,)
    )
    resp_counts = execute_query("""
        SELECT r.option_id, COUNT(*) AS votes
        FROM responses r
        JOIN (
            SELECT user_uuid, MAX(created_at) AS latest
            FROM responses
            WHERE question_code = %s
            GROUP BY user_uuid
        ) sub ON r.user_uuid = sub.user_uuid AND r.created_at = sub.latest
        WHERE r.question_code = %s AND r.option_id IS NOT NULL
        GROUP BY r.option_id
    """, (qcode, qcode))
    cb_counts = execute_query("""
        SELECT r.option_id, COUNT(*) AS votes
        FROM checkbox_responses r
        JOIN (
            SELECT user_uuid, MAX(created_at) AS latest
            FROM checkbox_responses
            WHERE question_code = %s
            GROUP BY user_uuid
        ) sub ON r.user_uuid = sub.user_uuid AND r.created_at = sub.latest
        WHERE r.question_code = %s AND r.option_id IS NOT NULL
        GROUP BY r.option_id
    """, (qcode, qcode))

    resp_map = {r["option_id"]: int(r["votes"]) for r in resp_counts} if resp_counts else {}
    cb_map = {r["option_id"]: int(r["votes"]) for r in cb_counts} if cb_counts else {}

    results = []
    for opt in option_rows:
        oid = opt["id"]
        results.append({
            "option_code": opt.get("option_code"),
            "votes": resp_map.get(oid, 0) + cb_map.get(oid, 0)
        })

    return {
        "status": "ok",
        "question_code": qcode,
        "results": results
    }





# ------------------ Age Validation ------------------
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