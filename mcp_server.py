# mcp_server.py
from flask import Flask, jsonify, request
from scan_sharepoint import run_scan
from metadata_db import export_csv
from generate_report import generate_summary
from send_email import send_report
from logger_db import init_logs
from metadata_db import fetch_all_rows, fetch_recent_items
import sqlite3

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/scan", methods=["POST"])
def scan():
    run_scan()
    return jsonify({"status": "success", "message": "Scan completed"})


@app.route("/metadata", methods=["GET"])
def metadata():
    conn = sqlite3.connect("sharepoint_metadata.db")
    cur = conn.cursor()
    result = cur.execute("SELECT * FROM files").fetchall()
    conn.close()

    return jsonify({
        "count": len(result),
        "files": result
    })

@app.route("/summary", methods=["GET"])
def summary():
    rows = fetch_all_rows()                     # all files from DB
    recent = fetch_recent_items(limit=10)       # last 10 updates

    # NEW FIELDS (must match your generate_summary function)
    new_files = []
    modified_files = []
    deleted_files = []

    report = generate_summary(
        rows=rows,
        recent_items=recent,
        new_files=new_files,
        modified_files=modified_files,
        deleted_files=deleted_files
    )

    return jsonify({"summary": report})



@app.route("/export", methods=["POST"])
def export():
    export_csv("metadata_export.csv")
    return jsonify({"status": "exported", "file": "metadata_export.csv"})


@app.route("/logs", methods=["GET"])
def logs():
    conn = sqlite3.connect("sharepoint_metadata.db")
    cur = conn.cursor()
    logs = cur.execute("SELECT timestamp, level, message FROM logs ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return jsonify({"logs": logs})


@app.route("/send_report", methods=["POST"])
def email_api():
    body = request.get_json()
    summary = body.get("summary")

    send_report(
        "keerthiyat@g3cyberspace.com",
        "SharePoint Summary Report",
        summary
    )

    return jsonify({"status": "sent"})


if __name__ == "__main__":
    init_logs()
    app.run(port=5005, debug=True)
