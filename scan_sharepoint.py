# scan_sharepoint.py

import requests
from auth_delegated import get_access_token
from metadata_db import init_db, upsert_file, should_update
from logger_db import init_logs, write_log
from generate_report import generate_summary
from send_email import send_report
from metadata_db import fetch_all_rows, fetch_recent_items
import time
from generate_report import utc_iso_to_ist


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
    init_db()
    init_logs()

    write_log("INFO", "Scan started.")
    changes_counter = [0]

    new_files = []
    modified_files = []
    deleted_files = []

    # Timestamp for deletions
    from datetime import datetime
    import pytz
    ist = pytz.timezone("Asia/Kolkata")
    scan_time = datetime.now(ist).strftime("%d-%b-%Y %I:%M:%S %p IST")

    try:
        items = get_children()
        write_log("INFO", f"Found {len(items)} items in root")

        current_ids = set()

        from metadata_db import get_all_ids, delete_record
        stored_ids = get_all_ids()

        # ---- PROCESS ALL ITEMS ----
        for item in items:
            source = resolve_remote_item(item)
            file_id = source.get("id")
            name = source.get("name")
            created_ts = source.get("createdDateTime")
            modified_ts = source.get("lastModifiedDateTime")

            current_ids.add(file_id)

            # NEW FILE
            if file_id not in stored_ids:
                new_files.append({
                    "name": name,
                    "timestamp": utc_iso_to_ist(created_ts)
                })

            # MODIFIED FILE
            elif should_update(file_id, modified_ts):
                modified_files.append({
                    "name": name,
                    "timestamp": utc_iso_to_ist(modified_ts)
                })

            # ALWAYS update DB
            upsert_file({
                "id": file_id,
                "name": name,
                "webUrl": source.get("webUrl"),
                "path": f"/root/{name}",
                "is_folder": 1 if "folder" in item else 0,
                "created": created_ts,
                "modified": modified_ts,
                "size": int(source.get("size", 0)),
            })

        # ---- DETECT DELETED FILES ----
        deleted_ids = stored_ids - current_ids

        for file_id in deleted_ids:
            deleted_files.append({
                "name": file_id,
                "timestamp": scan_time
            })
            delete_record(file_id)
            write_log("INFO", f"DELETED: {file_id}")
            changes_counter[0] += 1

        # ---- FETCH UPDATED DATA ----
        rows = fetch_all_rows()
        recent_items = fetch_recent_items(limit=10)

        # ---- CREATE THE FINAL SUMMARY ----
        summary = generate_summary(
            rows=rows,
            recent_items=recent_items,
            new_files=new_files,
            modified_files=modified_files,
            deleted_files=deleted_files
        )

        send_report(EMAIL_TARGET, EMAIL_SUBJECT, summary)
        write_log("INFO", "Email sent successfully.")

        print("Scan complete. Metadata updated and email sent.")

    except Exception as e:
        write_log("ERROR", f"Scan failed: {e}")
        raise


if __name__ == "__main__":
    run_scan()
