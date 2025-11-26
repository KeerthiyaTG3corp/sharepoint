# generate_report.py
import sqlite3
import datetime



DB_PATH = "sharepoint_metadata.db"

def generate_summary():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Total items
    total = cur.execute("SELECT count(*) FROM files").fetchone()[0]

    # Folders
    folders = cur.execute("SELECT count(*) FROM files WHERE is_folder=1").fetchone()[0]

    # Files
    files = total - folders

    # Largest file
    largest = cur.execute(
        "SELECT name, size FROM files WHERE is_folder=0 ORDER BY size DESC LIMIT 1"
    ).fetchone()

    # Recently modified
    recent = cur.execute(
        "SELECT name, modified FROM files WHERE is_folder=0 ORDER BY modified DESC LIMIT 5"
    ).fetchall()

    conn.close()

    summary = f"""
SharePoint Summary Report
Generated: {datetime.datetime.now().isoformat()}

Total Items: {total}
Folders: {folders}
Files: {files}

Largest File:
    {largest[0]} ({largest[1]} bytes)

Recently Modified Files:
"""
    for name, modified in recent:
        summary += f"    - {name} (modified {modified})\n"

    return summary


if __name__ == "__main__":
    print(generate_summary())
