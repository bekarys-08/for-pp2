import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
def get_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )

def setup_schema():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id       SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions (
            id            SERIAL PRIMARY KEY,
            player_id     INTEGER REFERENCES players(id),
            score         INTEGER   NOT NULL,
            level_reached INTEGER   NOT NULL,
            played_at     TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def get_or_create_player(username):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    row = cur.fetchone()
    if row:
        pid = row[0]
    else:
        cur.execute(
            "INSERT INTO players (username) VALUES (%s) RETURNING id",
            (username,)
        )
        pid = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return pid

def save_session(username, score, level):
    pid = get_or_create_player(username)
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
        (pid, score, level)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_personal_best(username):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT MAX(gs.score)
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        WHERE p.username = %s
    """, (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] or 0 if row else 0


def get_top10():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT p.username, gs.score, gs.level_reached,
               TO_CHAR(gs.played_at, 'DD Mon HH24:MI')
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        ORDER BY gs.score DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows