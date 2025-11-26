# logger_db.py
import sqlite3
import datetime

LOG_DB = "sharepoint_metadata.db"  # same DB as metadata to keep things simple

def init_logs():
    conn = sqlite3.connect(LOG_DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            level TEXT,
            message TEXT
        )
    """)
    conn.commit()
    conn.close()

def write_log(level, message):
    conn = sqlite3.connect(LOG_DB)
    cur = conn.cursor()
    now = datetime.datetime.now().isoformat()
    cur.execute("INSERT INTO logs (timestamp, level, message) VALUES (?, ?, ?)",
                (now, level, message))
    conn.commit()
    conn.close()
