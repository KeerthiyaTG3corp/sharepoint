import sqlite3
import os
import datetime

DB_PATH = "sharepoint_metadata.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            name TEXT,
            webUrl TEXT,
            path TEXT,
            is_folder INTEGER,
            created TEXT,
            modified TEXT,
            size INTEGER,
            last_seen TEXT
        )
    """)
    conn.commit()
    conn.close()

def upsert_file(info):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.datetime.now().isoformat()

    cur.execute("""
        INSERT INTO files (id, name, webUrl, path, is_folder, created, modified, size, last_seen)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            webUrl=excluded.webUrl,
            path=excluded.path,
            is_folder=excluded.is_folder,
            created=excluded.created,
            modified=excluded.modified,
            size=excluded.size,
            last_seen=excluded.last_seen
    """, (
        info.get("id"),
        info.get("name"),
        info.get("webUrl"),
        info.get("path"),
        info.get("is_folder"),
        info.get("created"),
        info.get("modified"),
        info.get("size"),
        now
    ))

    conn.commit()
    conn.close()

def should_update(item_id, new_modified):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT modified FROM files WHERE id=?", (item_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return True
    old_modified = row[0]
    if old_modified is None:
        return True
    return new_modified > old_modified

def export_csv(path="metadata_export.csv"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM files").fetchall()
    conn.close()

    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id","name","webUrl","path","is_folder","created","modified","size","last_seen"
        ])
        writer.writerows(rows)
