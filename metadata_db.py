# metadata_db.py
import sqlite3
import os

DB_NAME = "sharepoint_metadata.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            id TEXT PRIMARY KEY,
            name TEXT,
            webUrl TEXT,
            path TEXT,
            is_folder INTEGER,
            created TEXT,
            modified TEXT,
            size INTEGER
        )
    """)
    conn.commit()
    conn.close()


def upsert_file(record):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO metadata(id, name, webUrl, path, is_folder, created, modified, size)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            webUrl=excluded.webUrl,
            path=excluded.path,
            is_folder=excluded.is_folder,
            created=excluded.created,
            modified=excluded.modified,
            size=excluded.size
    """, (
        record["id"],
        record["name"],
        record["webUrl"],
        record["path"],
        record["is_folder"],
        record["created"],
        record["modified"],
        record["size"]
    ))

    conn.commit()
    conn.close()


def should_update(file_id, modified):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT modified FROM metadata WHERE id = ?", (file_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return True  # new file
    return row[0] != modified  # changed timestamp


# -------------------------------------------------------------------------
# ⭐ ADDED NOW — These were missing earlier
# -------------------------------------------------------------------------

def fetch_all_rows():
    """Return all file/folder metadata from DB as list of dicts."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, webUrl, path, is_folder, created, modified, size FROM metadata")
    rows = cur.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "name": r[1],
            "webUrl": r[2],
            "path": r[3],
            "is_folder": r[4],
            "created": r[5],
            "modified": r[6],
            "size": r[7]
        })
    return result


def fetch_recent_items(limit=10):
    """Return recently modified files."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT name, modified 
        FROM metadata 
        WHERE is_folder = 0 
        ORDER BY modified DESC 
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "name": r[0],
            "modified": r[1]
        })
    return result
def export_csv(file_path="sharepoint_metadata.csv"):
    """Export metadata table to a CSV file."""
    import csv
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, name, webUrl, path, is_folder, created, modified, size FROM metadata")
    rows = cur.fetchall()
    conn.close()

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "webUrl", "path", "is_folder", "created", "modified", "size"])
        writer.writerows(rows)

    return file_path

