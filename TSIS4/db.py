import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

def get_conn():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        print(f"DB Connection error: {e}")
        return None

def setup_schema():
    conn = get_conn()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id SERIAL PRIMARY KEY,
                player_id INTEGER REFERENCES players(id),
                username VARCHAR(50) NOT NULL,
                score INTEGER NOT NULL,
                level_reached INTEGER NOT NULL,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_score ON game_sessions(score DESC)")
        conn.commit()
        cur.close()
        conn.close()
        print("Database schema ready")
        return True
    except Exception as e:
        print(f"Schema error: {e}")
        return False

def save_game_result(username, score, level):
    print(f"Saving: {username}, {score}, {level}")
    
    conn = get_conn()
    if not conn:
        print("No connection")
        return False
    
    try:
        cur = conn.cursor()
        
        # Get or create player
        cur.execute("SELECT id FROM players WHERE username = %s", (username,))
        row = cur.fetchone()
        
        if row:
            player_id = row[0]
        else:
            cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
            player_id = cur.fetchone()[0]
        
        # Save game session
        cur.execute("""
            INSERT INTO game_sessions (player_id, username, score, level_reached)
            VALUES (%s, %s, %s, %s)
        """, (player_id, username, score, level))
        
        conn.commit()
        cur.close()
        conn.close()
        print("Save successful!")
        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False

def get_personal_best(username):
    conn = get_conn()
    if not conn:
        return 0
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE username = %s", (username,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else 0
    except Exception as e:
        print(f"Error getting personal best: {e}")
        return 0

def get_top10():
    conn = get_conn()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT username, score, level_reached, 
                   TO_CHAR(played_at, 'DD Mon HH24:MI') as played_date
            FROM game_sessions
            ORDER BY score DESC
            LIMIT 10
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        print(f"get_top10 returned {len(rows)} rows")
        return rows
    except Exception as e:
        print(f"Error getting top10: {e}")
        return []