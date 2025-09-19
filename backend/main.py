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

# ------------------ Unified vote handler (single, checkbox, other) ------------------
class VoteIn(BaseModel):
    user_uuid: str
    question_code: str
    # For single-choice either provide option_id OR other_text
    option_id: Optional[int] = None
    other_text: Optional[str] = None
    # add inside class VoteIn(BaseModel):
    option_select: Optional[str] = None   # e.g. "A", "B" — frontend currently sends this

    # For checkbox/multi-select:
    is_checkbox: Optional[bool] = False
    option_ids: Optional[List[int]] = None
    # optional weight per inserted row (defaults to 1.0)
    vote_weight: Optional[float] = 1.0

def _lock_key_for(user_uuid: str, question_code: str) -> int:
    """Deterministic 32-bit lock key for advisory locks."""
    return zlib.crc32(f"{user_uuid}|{question_code}".encode("utf-8"))

def _get_other_responses_columns():
    """Return set of column names in other_responses table."""
    rows = execute_query("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'other_responses'
    """)
    return {r["column_name"] for r in rows} if rows else set()

def _fetch_option_meta(conn_or_run, option_id):
    """Return option metadata dict or None. Accepts either a DB cursor (conn_or_run cursor) or uses execute_query."""
    try:
        # if a cursor-like object passed
        cur = conn_or_run
        cur.execute("SELECT id, option_select, option_code, option_text FROM options WHERE id = %s", (option_id,))
        r = cur.fetchone()
        if not r:
            return None
        return {"id": r[0], "option_select": r[1], "option_code": r[2], "option_text": r[3]}
    except Exception:
        # fallback to execute_query helper
        rows = execute_query("SELECT id, option_select, option_code, option_text FROM options WHERE id = %s", (option_id,))
        return rows[0] if rows else None

def _fetch_question_meta(conn_or_run, question_code):
    """Return question metadata (question_text, question_number, category_id, block_number) using cursor or execute_query."""
    try:
        cur = conn_or_run
        cur.execute("SELECT question_text, question_number, category_id, block_number FROM questions WHERE question_code = %s LIMIT 1", (question_code,))
        r = cur.fetchone()
        if not r:
            return None
        return {"question_text": r[0], "question_number": r[1], "category_id": r[2], "block_number": r[3]}
    except Exception:
        rows = execute_query("SELECT question_text, question_number, category_id, block_number FROM questions WHERE question_code = %s LIMIT 1", (question_code,))
        return rows[0] if rows else None

def _fetch_category_meta_by_id(conn_or_run, category_id):
    """Fetch category_name and category_text if available."""
    if category_id is None:
        return {"category_name": None, "category_text": None}
    try:
        cur = conn_or_run
        cur.execute("SELECT category_name, category_text FROM categories WHERE id = %s LIMIT 1", (category_id,))
        r = cur.fetchone()
        if not r:
            return {"category_name": None, "category_text": None}
        return {"category_name": r[0], "category_text": r[1]}
    except Exception:
        rows = execute_query("SELECT category_name, category_text FROM categories WHERE id = %s LIMIT 1", (category_id,))
        if rows:
            return {"category_name": rows[0].get("category_name"), "category_text": rows[0].get("category_text")}
        return {"category_name": None, "category_text": None}

@app.post("/api/vote")
def save_vote(payload: VoteIn):
    """
    Unified vote endpoint. Accepts:
      - single choice: { user_uuid, question_code, option_id } OR { user_uuid, question_code, other_text }
      - checkbox: { user_uuid, question_code, is_checkbox: true, option_ids: [..] }
      - optional vote_weight applied to each inserted row
    This handler:
      - uses advisory locks during single-choice upserts to avoid duplicate rows
      - inserts full snapshots into responses or checkbox_responses
      - stores long text into other_responses when other_text is provided (and inspects columns)
      - returns aggregates for response and checkbox counts per option
    """
    user_uuid = payload.user_uuid
    qcode = payload.question_code
    now = datetime.now(timezone.utc)   # tz-aware UTC
    vw = float(payload.vote_weight or 1.0)
   
   # If frontend sent option_select (like "A") but not option_id, resolve it to option_id
    if (payload.option_id is None) and getattr(payload, "option_select", None):
        sel = payload.option_select.strip()
        if sel:
            found = execute_query(
                "SELECT id FROM options WHERE question_code = %s AND UPPER(option_select) = %s LIMIT 1",
                (qcode, sel.upper())
            )
            if found:
                # support dict result or tuple
                first = found[0]
                payload.option_id = first["id"] if isinstance(first, dict) else first[0]
            # if not found, leave option_id=None so other_text can be used or validation will error later

    # Basic validation
    if not user_uuid or not qcode:
        raise HTTPException(status_code=422, detail="user_uuid and question_code required")

    # ---------- CHECKBOX MODE ----------
    if payload.is_checkbox:
        if not payload.option_ids or not isinstance(payload.option_ids, list):
            raise HTTPException(status_code=422, detail="option_ids (list) required for checkbox votes")

        # Delete previous checkbox responses for this user+question
        try:
            execute_query("DELETE FROM checkbox_responses WHERE user_uuid = %s AND question_code = %s", (user_uuid, qcode), fetch=False)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete previous checkbox_responses: {e}")

        # Fetch question meta once (fast)
        qmeta = _fetch_question_meta(None, qcode)
        qtext = qmeta.get("question_text") if qmeta else None
        qnum = qmeta.get("question_number") if qmeta else None
        cat_id = qmeta.get("category_id") if qmeta else None
        block_num = qmeta.get("block_number") if qmeta else None

        catmeta = _fetch_category_meta_by_id(None, cat_id) if cat_id else {"category_name": None, "category_text": None}

        insert_sql = """
        INSERT INTO checkbox_responses
          (user_uuid, question_code, question_text, question_number, category_id, category_name,
           category_text, option_id, option_select, option_code, option_text, block_number,
           created_at, weight, setup_question_code, setup_option_id, vote_weight)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        # For each option id, verify option exists and insert snapshot row
        for opt_id in payload.option_ids:
            opt_meta = _fetch_option_meta(None, opt_id)
            if not opt_meta:
                raise HTTPException(status_code=422, detail=f"option id {opt_id} not found")
            params = (
                user_uuid, qcode,
                qtext, qnum, cat_id,
                catmeta.get("category_name"), catmeta.get("category_text"),
                opt_meta["id"], opt_meta["option_select"], opt_meta["option_code"], opt_meta["option_text"],
                block_num,
                now, None, None, None, vw
            )
            try:
                execute_query(insert_sql, params, fetch=False)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed inserting checkbox_responses: {e}")

    # ---------- SINGLE-CHOICE MODE (option_id or other_text) ----------
    else:
        is_other = (payload.option_id is None) and (payload.other_text and payload.other_text.strip() != "")
        if not payload.option_id and not is_other:
            raise HTTPException(status_code=422, detail="Provide option_id for choice or other_text for 'Other' answer")

        # We'll attempt to get a real DB connection so we can use pg_advisory_xact_lock for safe upsert.
        conn = None
        cur = None
        try:
            conn = connection_pool.getconn()
            cur = conn.cursor()
            # Acquire transaction-scoped advisory lock for this user+question
            lock_key = _lock_key_for(user_uuid, qcode)
            cur.execute("SELECT pg_advisory_xact_lock(%s)", (lock_key,))

            # Check if a responses row exists (and lock it)
            cur.execute("SELECT id FROM responses WHERE user_uuid = %s AND question_code = %s LIMIT 1 FOR UPDATE", (user_uuid, qcode))
            existing = cur.fetchone()  # (id,) or None

            # Fetch question metadata
            cur.execute("SELECT question_text, question_number, category_id, block_number FROM questions WHERE question_code = %s LIMIT 1", (qcode,))
            qrow = cur.fetchone()
            if qrow:
                q_text, q_number, category_id, block_number = qrow[0], qrow[1], qrow[2], qrow[3]
            else:
                q_text = q_number = category_id = block_number = None

            catmeta = _fetch_category_meta_by_id(cur, category_id) if category_id else {"category_name": None, "category_text": None}

            if is_other:
                other_text = payload.other_text.strip()
                # update or insert responses row with marker for Other
                if existing:
                    rid = existing[0]
                    cur.execute("""
                        UPDATE responses
                        SET option_id = NULL,
                            option_select = %s,
                            option_code = %s,
                            option_text = %s,
                            vote_weight = %s,
                            created_at = COALESCE(created_at, %s)
                        WHERE id = %s
                    """, ("Other", "OTHER", other_text[:500], vw, now, rid))
                else:
                    cur.execute("""
                        INSERT INTO responses
                          (user_uuid, question_code, question_text, question_number, category_id, category_name, category_text,
                           option_id, option_select, option_code, option_text, block_number, created_at, setup_question_code,
                           setup_option_id, vote_weight)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        user_uuid, qcode,
                        q_text, q_number, category_id, catmeta.get("category_name"), catmeta.get("category_text"),
                        None, "Other", "OTHER", other_text[:500],
                        block_number, now, None, None, vw
                    ))

                # Insert into other_responses table (only columns that exist)
                other_cols = _get_other_responses_columns()
                insert_cols = []
                insert_vals = []
                if "user_uuid" in other_cols:
                    insert_cols.append("user_uuid"); insert_vals.append(user_uuid)
                if "question_code" in other_cols:
                    insert_cols.append("question_code"); insert_vals.append(qcode)
                if "question_text" in other_cols:
                    insert_cols.append("question_text"); insert_vals.append(q_text)
                if "question_number" in other_cols:
                    insert_cols.append("question_number"); insert_vals.append(q_number)
                if "category_id" in other_cols:
                    insert_cols.append("category_id"); insert_vals.append(category_id)
                if "category_name" in other_cols:
                    insert_cols.append("category_name"); insert_vals.append(catmeta.get("category_name"))
                if "category_text" in other_cols:
                    insert_cols.append("category_text"); insert_vals.append(catmeta.get("category_text"))
                if "block_number" in other_cols:
                    insert_cols.append("block_number"); insert_vals.append(block_number)
                # pick either "other_text" or "text" commonly used
                if "other_text" in other_cols:
                    insert_cols.append("other_text"); insert_vals.append(other_text)
                elif "text" in other_cols:
                    insert_cols.append("text"); insert_vals.append(other_text)
                if "created_at" in other_cols:
                    insert_cols.append("created_at"); insert_vals.append(now)
                if "vote_weight" in other_cols:
                    insert_cols.append("vote_weight"); insert_vals.append(vw)
                elif "weight" in other_cols:
                    insert_cols.append("weight"); insert_vals.append(vw)

                if insert_cols:
                    placeholders = ",".join(["%s"] * len(insert_vals))
                    cols_sql = ",".join(insert_cols)
                    cur.execute(f"INSERT INTO other_responses ({cols_sql}) VALUES ({placeholders})", tuple(insert_vals))

            else:
                # Normal option_id path
                cur.execute("SELECT id, option_select, option_code, option_text FROM options WHERE id = %s LIMIT 1", (payload.option_id,))
                optrow = cur.fetchone()
                if not optrow:
                    conn.rollback()
                    raise HTTPException(status_code=422, detail=f"option id {payload.option_id} not found")
                opt_id, opt_select, opt_code, opt_text = optrow[0], optrow[1], optrow[2], optrow[3]

                if existing:
                    rid = existing[0]
                    cur.execute("""
                        UPDATE responses
                        SET option_id = %s,
                            option_select = %s,
                            option_code = %s,
                            option_text = %s,
                            vote_weight = %s,
                            created_at = COALESCE(created_at, %s)
                        WHERE id = %s
                    """, (opt_id, opt_select, opt_code, opt_text, vw, now, rid))
                else:
                    cur.execute("""
                        INSERT INTO responses
                          (user_uuid, question_code, question_text, question_number, category_id, category_name, category_text,
                           option_id, option_select, option_code, option_text, block_number, created_at, setup_question_code,
                           setup_option_id, vote_weight)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        user_uuid, qcode,
                        q_text, q_number, category_id, catmeta.get("category_name"), catmeta.get("category_text"),
                        opt_id, opt_select, opt_code, opt_text,
                        block_number, now, None, None, vw
                    ))

            # commit transaction (advisory lock released at transaction end)
            conn.commit()

        except HTTPException:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise HTTPException(status_code=500, detail=f"DB error saving vote: {e}")
        finally:
            if cur:
                try:
                    cur.close()
                except Exception:
                    pass
            if conn:
                try:
                    connection_pool.putconn(conn)
                except Exception:
                    pass

    # ---------- AGGREGATES: compute votes per option from both responses & checkbox_responses ----------
    # canonical options for the question (so frontend sees all options even if zero votes)
    option_rows = execute_query("SELECT id, option_select, option_code, option_text FROM options WHERE question_code = %s ORDER BY id", (qcode,))

    resp_counts = execute_query("""
        SELECT option_id, COALESCE(SUM(COALESCE(vote_weight,1.0)),0) AS votes
        FROM responses
        WHERE question_code = %s AND option_id IS NOT NULL
        GROUP BY option_id
    """, (qcode,))

    cb_counts = execute_query("""
        SELECT option_id, COALESCE(SUM(COALESCE(vote_weight,1.0)),0) AS votes
        FROM checkbox_responses
        WHERE question_code = %s AND option_id IS NOT NULL
        GROUP BY option_id
    """, (qcode,))

    resp_map = {r["option_id"]: float(r["votes"]) for r in resp_counts} if resp_counts else {}
    cb_map = {r["option_id"]: float(r["votes"]) for r in cb_counts} if cb_counts else {}

    single_choice_aggregates = []
    checkbox_aggregates = []
    for opt in option_rows:
        oid = opt["id"]
        single_choice_aggregates.append({
            "option_id": oid,
            "option_select": opt.get("option_select"),
            "option_code": opt.get("option_code"),
            "option_text": opt.get("option_text"),
            "votes": resp_map.get(oid, 0.0)
        })
        checkbox_aggregates.append({
            "option_id": oid,
            "option_select": opt.get("option_select"),
            "option_code": opt.get("option_code"),
            "option_text": opt.get("option_text"),
            "votes": cb_map.get(oid, 0.0)
        })

    return {
        "status": "ok",
        "question_code": qcode,
        "single_choice_aggregates": single_choice_aggregates,
        "checkbox_aggregates": checkbox_aggregates
    }





# add near your other GET endpoints (e.g. under /api/options)


@app.get("/api/results/{question_code}")
def get_results_backcompat(question_code: str):
    """
    Backwards-compatible results endpoint.

    Returns:
      - single_choice_aggregates: modern shape (option_select, option_code, option_text, votes)
      - checkbox_aggregates: modern checkbox shape
      - results: legacy shape (array of { option_select, count }) for old frontends
      - total_responses: numeric total
    """
    try:
        # canonical options (ordered)
        option_rows = execute_query(
            "SELECT id, option_select, option_code, option_text FROM options WHERE question_code = %s ORDER BY id",
            (question_code,)
        ) or []

        # counts by normalized option_select (preferred)
        resp_sel_counts = execute_query(
            """
            SELECT COALESCE(UPPER(TRIM(option_select)), 'OTHER') AS sel_norm,
                   COALESCE(SUM(COALESCE(vote_weight,1.0)),0) AS votes
            FROM responses
            WHERE question_code = %s
            GROUP BY COALESCE(UPPER(TRIM(option_select)), 'OTHER')
            """,
            (question_code,)
        ) or []
        resp_map_sel = { r["sel_norm"]: float(r["votes"]) for r in resp_sel_counts }

        # counts by option_id (fallback)
        resp_id_counts = execute_query(
            """
            SELECT option_id, COALESCE(SUM(COALESCE(vote_weight,1.0)),0) AS votes
            FROM responses
            WHERE question_code = %s AND option_id IS NOT NULL
            GROUP BY option_id
            """,
            (question_code,)
        ) or []
        resp_map_id = { (int(r["option_id"]) if r["option_id"] is not None else None): float(r["votes"]) for r in resp_id_counts }

        # checkbox counts by normalized option_select (we'll conditionally use this)
        cb_sel_counts = execute_query(
            """
            SELECT COALESCE(UPPER(TRIM(option_select)), 'OTHER') AS sel_norm,
                   COALESCE(SUM(COALESCE(vote_weight,1.0)),0) AS votes
            FROM checkbox_responses
            WHERE question_code = %s
            GROUP BY COALESCE(UPPER(TRIM(option_select)), 'OTHER')
            """,
            (question_code,)
        ) or []
        cb_map_sel = { r["sel_norm"]: float(r["votes"]) for r in cb_sel_counts }

        # Build modern aggregates for canonical options
        single_choice_aggregates = []
        checkbox_aggregates = []
        seen_sel_keys = set()
        seen_option_ids = set()

        for opt in option_rows:
            oid = opt.get("id")
            raw_sel = (opt.get("option_select") or "")
            key = raw_sel.strip().upper() if raw_sel else "OTHER"

            # pick votes: prefer normalized option_select counts, fallback to option_id
            votes = resp_map_sel.get(key, 0.0)
            if votes == 0 and oid is not None:
                votes = resp_map_id.get(oid, 0.0)

            single_choice_aggregates.append({
                "option_id": oid,
                "option_select": raw_sel,
                "option_code": opt.get("option_code"),
                "option_text": opt.get("option_text"),
                "votes": votes
            })

            # checkbox (canonical) — use normalized select counts
            cb_votes = cb_map_sel.get(key, 0.0)
            checkbox_aggregates.append({
                "option_id": oid,
                "option_select": raw_sel,
                "option_code": opt.get("option_code"),
                "option_text": opt.get("option_text"),
                "votes": cb_votes
            })

            seen_sel_keys.add(key)
            if oid is not None:
                seen_option_ids.add(oid)

        # Append any extra response buckets (normalized select) not in canonical options
        for sel_norm, votes in resp_map_sel.items():
            if sel_norm not in seen_sel_keys:
                single_choice_aggregates.append({
                    "option_id": None,
                    "option_select": sel_norm,
                    "option_code": sel_norm,
                    "option_text": sel_norm,
                    "votes": votes
                })
                seen_sel_keys.add(sel_norm)

        # Append any orphan option_id counts that are not in canonical options
        for opt_id, votes in resp_map_id.items():
            if opt_id not in seen_option_ids:
                single_choice_aggregates.append({
                    "option_id": opt_id,
                    "option_select": None,
                    "option_code": None,
                    "option_text": None,
                    "votes": votes
                })
                seen_option_ids.add(opt_id)

        # Total responses
        total_row = execute_query(
            "SELECT COALESCE(SUM(COALESCE(vote_weight,1.0)),0) AS total FROM responses WHERE question_code = %s",
            (question_code,)
        )
        total_responses = float(total_row[0]["total"]) if total_row else 0.0

        # --- BUILD LEGACY 'results' ARRAY for backward compatibility ---
        # legacy array: [{ option_select, count, option_text? }]
        legacy_results = []
        # prefer canonical option order
        if option_rows:
            for opt in option_rows:
                oid = opt.get("id")
                sel = (opt.get("option_select") or "").strip()
                key = sel.upper() if sel else "OTHER"
                # find corresponding votes from modern aggregates (match by option_select or option_id)
                votes = 0.0
                # search in single_choice_aggregates for matching entry
                for a in single_choice_aggregates:
                    # match by option_id OR normalized option_select
                    if a.get("option_id") == oid:
                        votes = float(a.get("votes", 0.0))
                        break
                    if a.get("option_select") and a.get("option_select").strip().upper() == key:
                        votes = float(a.get("votes", 0.0))
                        break
                legacy_results.append({
                    "option_select": sel,
                    "count": votes,
                    "option_text": opt.get("option_text")
                })
        else:
            # no canonical options: emit buckets found in single_choice_aggregates
            for a in single_choice_aggregates:
                legacy_results.append({
                    "option_select": a.get("option_select") or (a.get("option_code") or str(a.get("option_id") or '')),
                    "count": float(a.get("votes") or 0.0),
                    "option_text": a.get("option_text")
                })

        # Build final payload — include both modern and legacy shapes
        payload = {
            "status": "ok",
            "question_code": question_code,
            "total_responses": total_responses,
            "single_choice_aggregates": single_choice_aggregates,
            "checkbox_aggregates": checkbox_aggregates,
            # legacy compatibility field used by older frontends:
            "results": legacy_results
        }

        return payload

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch results: {e}")




# ------------------ "Other" text vote (kept for backward compat) ------------------
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
