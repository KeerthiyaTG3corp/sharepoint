# mcp_server.py
from flask import Flask, jsonify, request
from scan_sharepoint import run_scan
from metadata_db import export_csv
from generate_report import generate_summary
from send_email import send_report
from logger_db import init_logs
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
    report = generate_summary()
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
    report = generate_summary()
    send_report(
        "keerthiyat@g3cyberspace.com",  # your email
        "SharePoint Summary Report",
        report
    )
    return jsonify({"status": "sent"})


if __name__ == "__main__":
    init_logs()
    app.run(port=5005, debug=True)
