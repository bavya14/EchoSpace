import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).with_name("echospace.db")

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS mood_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT NOT NULL,
            mood TEXT NOT NULL,
            tags TEXT DEFAULT '',
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL,
            hidden INTEGER DEFAULT 0
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            reaction TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(post_id) REFERENCES posts(id)
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(post_id) REFERENCES posts(id)
        )""")

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def add_entry(entry_date, mood, tags, note):
    with connect() as conn:
        conn.execute("INSERT INTO mood_entries(entry_date,mood,tags,note,created_at) VALUES(?,?,?,?,?)",
                     (entry_date, mood, tags, note, now()))

def get_entries():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM mood_entries ORDER BY entry_date DESC, id DESC").fetchall()
    return [dict(r) for r in rows]

def add_post(category, body):
    with connect() as conn:
        conn.execute("INSERT INTO posts(category,body,created_at) VALUES(?,?,?)", (category, body, now()))

def get_posts():
    with connect() as conn:
        posts = conn.execute("SELECT * FROM posts WHERE hidden=0 ORDER BY id DESC").fetchall()
        result = []
        for p in posts:
            counts = conn.execute("SELECT reaction,COUNT(*) AS n FROM reactions WHERE post_id=? GROUP BY reaction", (p["id"],)).fetchall()
            result.append({**dict(p), "reactions": {r["reaction"]: r["n"] for r in counts}})
    return result

def add_reaction(post_id, reaction):
    with connect() as conn:
        conn.execute("INSERT INTO reactions(post_id,reaction,created_at) VALUES(?,?,?)", (post_id, reaction, now()))

def flag_post(post_id, reason):
    with connect() as conn:
        conn.execute("INSERT INTO reports(post_id,reason,created_at) VALUES(?,?,?)", (post_id, reason, now()))

def get_stats():
    with connect() as conn:
        posts = conn.execute("SELECT COUNT(*) n FROM posts WHERE hidden=0").fetchone()["n"]
        reactions = conn.execute("SELECT COUNT(*) n FROM reactions").fetchone()["n"]
        entries = conn.execute("SELECT COUNT(*) n FROM mood_entries").fetchone()["n"]
    return {"posts": posts, "reactions": reactions, "entries": entries}
