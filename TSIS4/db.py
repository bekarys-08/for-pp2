import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

def get_conn():
    """Create database connection"""
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
        print(f"Database connection error: {e}")
        return None

def setup_schema():
    """Create tables if they don't exist"""
    conn = get_conn()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # Create players table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            );
        """)
        
        # Create game_sessions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id SERIAL PRIMARY KEY,
                player_id INTEGER REFERENCES players(id),
                score INTEGER NOT NULL,
                level_reached INTEGER NOT NULL,
                played_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Create indexes for better performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_game_sessions_score ON game_sessions(score DESC);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_players_username ON players(username);")
        
        conn.commit()
        cur.close()
        conn.close()
        print("Database schema created successfully")
        return True
    except Exception as e:
        print(f"Error creating schema: {e}")
        return False

def get_or_create_player(username):
    """Get player ID or create new player"""
    conn = get_conn()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM players WHERE username = %s", (username,))
        row = cur.fetchone()
        
        if row:
            player_id = row[0]
        else:
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) RETURNING id",
                (username,)
            )
            player_id = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        conn.close()
        return player_id
    except Exception as e:
        print(f"Error in get_or_create_player: {e}")
        return None

def save_session(username, score, level):
    """Save game result to database"""
    player_id = get_or_create_player(username)
    if not player_id:
        return False
    
    conn = get_conn()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO game_sessions (player_id, score, level_reached) 
            VALUES (%s, %s, %s)
        """, (player_id, score, level))
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"Game saved - Player: {username}, Score: {score}, Level: {level}")
        return True
    except Exception as e:
        print(f"Error saving session: {e}")
        return False

def get_personal_best(username):
    """Get player's best score"""
    conn = get_conn()
    if not conn:
        return 0
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT MAX(gs.score)
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            WHERE p.username = %s
        """, (username,))
        
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        return row[0] if row and row[0] else 0
    except Exception as e:
        print(f"Error getting personal best: {e}")
        return 0

def get_top10():
    """Get top 10 scores for leaderboard"""
    conn = get_conn()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.username, gs.score, gs.level_reached,
                   TO_CHAR(gs.played_at, 'DD Mon HH24:MI') as played_date
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            ORDER BY gs.score DESC
            LIMIT 10
        """)
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error getting top 10: {e}")
        return []