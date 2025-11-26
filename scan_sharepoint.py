# scan_sharepoint.py
"""
FINAL VERSION FOR KEERTHI (UPDATED)
✔ Scans ROOT of your SharePoint drive
✔ Recursively scans all folders & files
✔ No 404 errors
✔ ALWAYS sends email after scan (even if no changes)
✔ Works cleanly with MCP server
"""

import requests
from auth_delegated import get_access_token
from metadata_db import init_db, upsert_file, should_update
from logger_db import init_logs, write_log
from generate_report import generate_summary
from send_email import send_report
import time

GRAPH = "https://graph.microsoft.com/v1.0"

# Your SharePoint drive ID
DRIVE_ID = "b!kpAbDK4p4ESX1ZSH0dcYsqxBc_weM9BNm0ybtn1kW2q_uiSxaLMWT7k9P9cCdYTh"

# Email settings
EMAIL_TARGET = "keerthiyat@g3cyberspace.com"
EMAIL_SUBJECT = "SharePoint Summary Report (Auto)"


def build_headers():
    token = get_access_token()
    return {"Authorization": f"Bearer {token}"}


def get_children(parent_id=None):
    """
    CORRECT for your SharePoint structure:
    - All files/folders are directly in the root
    - No parent folder like 'Shared Documents'
    """
    headers = build_headers()

    if parent_id is None:
        url = f"{GRAPH}/drives/{DRIVE_ID}/root/children"
    else:
        url = f"{GRAPH}/drives/{DRIVE_ID}/items/{parent_id}/children"

    items = []
    while url:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()

        items.extend(data.get("value", []))
        url = data.get("@odata.nextLink")  # pagination

    return items


def resolve_remote_item(item):
    """
    Handles shortcut files or linked items.
    """
    if "remoteItem" not in item:
        return item

    remote = item["remoteItem"]
    return {
        "id": item.get("id"),
        "name": item.get("name") or remote.get("name"),
        "webUrl": remote.get("webUrl"),
        "createdDateTime": remote.get("createdDateTime"),
        "lastModifiedDateTime": remote.get("lastModifiedDateTime"),
        "size": remote.get("size", 0),
    }


def scan_folder(item, parent_path, changes_counter):
    """
    Recursively scans folders and files.
    """
    source = resolve_remote_item(item)
    name = source.get("name")
    path = f"{parent_path}/{name}"

    is_folder = "folder" in item

    # Build DB record
    record = {
        "id": item.get("id"),
        "name": name,
        "webUrl": source.get("webUrl"),
        "path": path,
        "is_folder": 1 if is_folder else 0,
        "created": source.get("createdDateTime"),
        "modified": source.get("lastModifiedDateTime"),
        "size": int(source.get("size", 0)),
    }

    # Check if modified/new
    if should_update(record["id"], record["modified"]):
        upsert_file(record)
        write_log("INFO", f"UPDATED: {path}")
        changes_counter[0] += 1
    else:
        write_log("DEBUG", f"No change: {path}")

    # Recurse into subfolders
    if is_folder:
        children = get_children(item.get("id"))
        for child in children:
            scan_folder(child, path, changes_counter)


def run_scan():
    """
    MAIN SCAN PROCESS
    """
    init_db()
    init_logs()

    write_log("INFO", "Scan started.")
    changes_counter = [0]

    try:
        items = get_children()
        write_log("INFO", f"Found {len(items)} items in root")

        for item in items:
            scan_folder(item, "/root", changes_counter)

        write_log("INFO", f"Scan complete. Changes found: {changes_counter[0]}")
        print("Scan complete. Metadata updated.")

        # ⭐ ALWAYS SEND EMAIL (your request)
        summary = generate_summary()
        send_report(EMAIL_TARGET, EMAIL_SUBJECT, summary)
        write_log("INFO", "Email sent (forced mode).")

    except Exception as e:
        write_log("ERROR", f"Scan failed: {e}")
        raise


if __name__ == "__main__":
    run_scan()
