# main.py
# main.py (updated: unified /api/vote handler that uses responses, checkbox_responses, other_responses)
from fastapi import FastAPI, HTTPException, Request
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
def get_metadata(q_code, opt_select=None):
    if opt_select:
        rows = execute_query(
            """
            SELECT q.question_text, q.question_number,
                   q.category_id, c.category_name, c.category_text, q.block_number,
                   o.option_select, o.option_code, o.option_text
            FROM questions q
            JOIN categories c ON q.category_id = c.id
            JOIN options o ON q.question_code = o.question_code
            WHERE q.question_code = %s AND o.option_select = %s
            """,
            (q_code, opt_select)
        )
    else:
        rows = execute_query(
            """
            SELECT q.question_text, q.question_number,
                   q.category_id, c.category_name, c.category_text, q.block_number
            FROM questions q
            JOIN categories c ON q.category_id = c.id
            WHERE q.question_code = %s
            """,
            (q_code,)
        )
    return rows[0] if rows else None


# ----------------------------
# Vote submission (single, checkbox, free text)
# ----------------------------
# ----------------------------
# Submit vote
# ----------------------------
@app.post("/api/vote")
async def submit_vote(request: Request):
    # Get raw request body
    raw_body = await request.body()
    print("=== DEBUG RAW REQUEST BODY ===")
    print(raw_body.decode('utf-8'))
    print("=============================")
    
    # Parse JSON manually to see what we actually receive
    import json
    vote = json.loads(raw_body.decode('utf-8'))
    """
    Accepts a vote payload and stores it in the appropriate table:
      - Single-choice → responses
      - Checkbox → checkbox_responses (with vote_weight)
      - Other → other_responses (and placeholder in chart)
    """

    user_uuid = vote.get("user_uuid")
    question_code = vote.get("question_code")
    option_select = vote.get("option_select")
    option_selects = vote.get("option_selects", [])  # plural form
    other_text = vote.get("other_text")

 # ✅ Add this debug line right here:
    print("=== DEBUG VOTE SUBMISSION ===")
    print("DEBUG RAW PAYLOAD:", vote)
    print("DEBUG option_select:", option_select)
    print("DEBUG option_selects:", option_selects)
    print("DEBUG other_text:", other_text)
    print("DEBUG option_selects type:", type(option_selects))
    print("DEBUG option_selects length:", len(option_selects) if option_selects else "None")




    OTHER_KEY = "OTHER"
    def _is_other(v): 
        return isinstance(v, str) and v.strip().upper() == OTHER_KEY

    # --- Normalize "Other" values ---
    if option_select and _is_other(option_select):
        option_select = OTHER_KEY

    if option_selects:
        option_selects = [OTHER_KEY if _is_other(v) else v for v in option_selects]

    if other_text:
        other_text = other_text.strip()

    # --- Debug logging ---
    print("DEBUG payload:", vote)
    print("DEBUG option_select type:", type(option_select))
    print("DEBUG option_select value:", option_select)
    print("DEBUG option_selects:", option_selects)

    # --- Normalize payloads ---
    # Sometimes frontend sends checkbox list under option_select instead of option_selects
    if isinstance(option_select, list):
        option_selects = option_select
        option_select = None

    # Lookup question metadata
    meta = get_metadata(question_code)

    # --- Handle checkbox votes ---
    if option_selects:
        print("=== PROCESSING CHECKBOX VOTES ===")
        print("DEBUG option_selects:", option_selects)
        n = len(option_selects)
        print("DEBUG n (length):", n)
        if n == 0:
            raise HTTPException(status_code=400, detail="No checkbox options provided")
        weight = 1.0 / n
        print("DEBUG weight:", weight)
        for opt in option_selects:
            print(f"DEBUG Processing option: {opt}")
            # Always insert the vote itself
            execute_query(
                """
                INSERT INTO checkbox_responses
                (user_uuid, question_code, question_text, question_number,
                category_id, category_name, category_text, block_number,
                option_id, option_select, option_code, option_text,
                weight, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
                """,
                (
                    user_uuid, question_code, meta["question_text"], meta["question_number"],
                    meta["category_id"], meta["category_name"], meta["category_text"], meta["block_number"],
                    None, opt, f"{question_code}_{opt}", opt, weight
                ),
                fetch=False
            )

            # ✅ If "OTHER" was selected and free text exists, also store it
            if opt == "OTHER" and other_text:
                execute_query(
                    """
                    INSERT INTO other_responses
                    (user_uuid, question_code, question_text, question_number,
                    category_id, category_name, category_text, block_number,
                    other_text, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
                    """,
                    (
                        user_uuid, question_code,
                        meta["question_text"], meta["question_number"],
                        meta["category_id"], meta["category_name"], meta["category_text"], meta["block_number"],
                        other_text,
                    ),
                    fetch=False,
                )

        # ✅ Always return here
        return {"message": "Checkbox vote(s) recorded", "question_code": question_code}


    # --- Handle Other-text only (no option selected) ---
    if other_text and not option_select and not option_selects:
        # save the free text
        execute_query(
            """
            INSERT INTO other_responses
            (user_uuid, question_code, question_text, question_number,
            category_id, category_name, category_text, block_number,
            other_text, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            """,
            (
                user_uuid, question_code,
                meta["question_text"], meta["question_number"],
                meta["category_id"], meta["category_name"], meta["category_text"], meta["block_number"],
                other_text,
            ),
            fetch=False,
        )      
        # create a bar so charts show OTHER
        execute_query(
            """
            INSERT INTO responses
            (user_uuid, question_code, question_text, question_number,
            category_id, category_name, category_text, block_number,
            option_id, option_select, option_code, option_text,
            created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            """,
            (
                user_uuid, question_code,
                meta["question_text"], meta["question_number"],
                meta["category_id"], meta["category_name"], meta["category_text"], meta["block_number"],
                None, OTHER_KEY, f"{question_code}_{OTHER_KEY}", "Other",
            ),
            fetch=False,
        )
        return {"message": "Other-only response recorded", "question_code": question_code}


    # --- Handle single-choice votes ---
    if option_select:
        execute_query(
            """
            INSERT INTO responses
            (user_uuid, question_code, question_text, question_number,
            category_id, category_name, category_text, block_number,
            option_id, option_select, option_code, option_text,
            created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            """,
            (
                user_uuid, question_code, meta["question_text"], meta["question_number"],
                meta["category_id"], meta["category_name"], meta["category_text"], meta["block_number"],
                None, option_select, f"{question_code}_{option_select}", option_select
            ),
            fetch=False
        )

        # If user selected OTHER and typed free text, also store it
        if option_select == "OTHER" and other_text:
            execute_query(
                """
                INSERT INTO other_responses
                (user_uuid, question_code, question_text, question_number,
                category_id, category_name, category_text, block_number,
                other_text, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
                """,
                (
                    user_uuid, question_code,
                    meta["question_text"], meta["question_number"],
                    meta["category_id"], meta["category_name"], meta["category_text"], meta["block_number"],
                    other_text,
                ),
                fetch=False,
            )

        # ✅ Always return here (so frontend shows text box, chart updates, no 400)
        return {"message": "Single-choice vote recorded", "question_code": question_code}


    
    # --- If nothing matched ---
    raise HTTPException(status_code=400, detail="Invalid vote payload")



# ----------------------------
# Results aggregation
# ----------------------------
# ----------------------------
# Results aggregation
# ----------------------------
@app.get("/api/results/{question_code}")
def get_results(question_code: str):
    """
    Aggregates results for a question:
      - Single-choice from responses
      - Checkbox from checkbox_responses
      - Total responses reported as integer (number of distinct users)
    """

    # Get all option definitions for the question
    option_rows = execute_query(
        """
        SELECT option_select, option_code, option_text
        FROM options
        WHERE question_code = %s
        ORDER BY id
        """,
        (question_code,)
    ) or []

    # Single-choice counts
    single_counts = execute_query(
        """
        SELECT option_select, COUNT(*)::float as votes
        FROM responses
        WHERE question_code = %s
        GROUP BY option_select
        """,
        (question_code,)
    ) or []

    # Checkbox counts (safe cast + handle empty case)
    checkbox_counts = execute_query(
        """
        SELECT option_select, COALESCE(SUM(weight),0)::float as votes
        FROM checkbox_responses
        WHERE question_code = %s
        GROUP BY option_select
        """,
        (question_code,)
    ) or []

    print(f"=== RESULTS DEBUG for {question_code} ===")
    print(f"Single counts: {single_counts}")
    print(f"Checkbox counts: {checkbox_counts}")

    # --- Merge counts into one dict ---
    counts = {}
    for row in single_counts + checkbox_counts:
        sel = row["option_select"]
        counts[sel] = counts.get(sel, 0) + row["votes"]

    # --- Build results list from canonical options ---
    results = []
    for opt in option_rows:
        sel = opt["option_select"]
        votes = counts.get(sel, 0)
        results.append({
            "option_select": opt["option_select"],  # keep display form from options table
            "option_code": opt["option_code"],
            "option_text": opt["option_text"],
            "votes": votes
        })

    # --- Total responses as integer (distinct users across both tables) ---
    total_result = execute_query(
        """
        SELECT COUNT(DISTINCT user_uuid) AS n FROM (
            SELECT user_uuid FROM responses WHERE question_code = %s
            UNION
            SELECT user_uuid FROM checkbox_responses WHERE question_code = %s
        ) AS combined_votes
        """,
        (question_code, question_code)
    )
    
    total = int(total_result[0]["n"]) if total_result else 0
    print(f"Total result: {total_result}")
    print(f"Calculated total: {total}")
    print(f"Final results: {results}")

    return {
        "question_code": question_code,
        "results": results,
        "total_responses": total
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