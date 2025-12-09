# generate_report.py
"""
Generate a human-friendly SharePoint summary report.
All timestamps are converted to IST (Asia/Kolkata).
"""

from datetime import datetime
import pytz

# Helper: convert UTC ISO timestamp (with or without 'Z') to IST formatted string
def utc_iso_to_ist(iso_ts: str) -> str:
    """
    Converts an ISO UTC timestamp (e.g. "2025-11-25T06:36:10Z" or "2025-11-25T06:36:10")
    to a readable IST string like "25-Nov-2025 11:06 AM IST".
    If parsing fails, returns the original string.
    """
    if not iso_ts:
        return iso_ts
    try:
        # normalize trailing Z
        s = iso_ts.rstrip()
        if s.endswith("Z"):
            s = s[:-1]
        # Try parsing with microseconds if present, else without
        dt = None
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(s, fmt)
                break
            except ValueError:
                continue
        if dt is None:
            # can't parse, return original
            return iso_ts

        # localize as UTC, convert to IST
        utc = pytz.timezone("UTC")
        ist_tz = pytz.timezone("Asia/Kolkata")
        dt_utc = utc.localize(dt)
        dt_ist = dt_utc.astimezone(ist_tz)

        return dt_ist.strftime("%d-%b-%Y %I:%M %p IST")
    except Exception:
        return iso_ts
def generate_summary(rows=None, recent_items=None,
                     new_files=None, modified_files=None, deleted_files=None):

    new_files = new_files or []
    modified_files = modified_files or []
    deleted_files = deleted_files or []

    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist).strftime("%d-%b-%Y %I:%M:%S %p IST")

    rows = rows or []
    recent_items = recent_items or []

    total_items = len(rows)
    folder_count = sum(1 for r in rows if r.get("is_folder"))
    file_count = total_items - folder_count

    # Largest file
    largest_name = "N/A"
    largest_size = 0
    for r in rows:
        try:
            sz = int(r.get("size", 0) or 0)
        except:
            sz = 0
        if sz > largest_size:
            largest_size = sz
            largest_name = r.get("name", "unknown")

    # Format sections (new / modified / deleted)
    def format_section(items, label):
        if not items:
            return "    None"
        return "\n".join([f"    - {i['name']} ({label} {i['timestamp']})" for i in items])

    new_section = format_section(new_files, "created")
    mod_section = format_section(modified_files, "modified")
    del_section = format_section(deleted_files, "deleted")

    # Recently modified files
    recent_lines = []
    for item in recent_items:
        name = item.get("name")
        modified_ist = utc_iso_to_ist(item.get("modified"))
        recent_lines.append(f"    - {name} (modified {modified_ist})")

    recent_section = "\n".join(recent_lines) if recent_lines else "    None"

    summary = f"""SharePoint Summary Report
Generated: {now_ist}

Total Items: {total_items}
Folders: {folder_count}
Files: {file_count}

Largest File:
    {largest_name} ({largest_size} bytes)

New Files:
{new_section}

Modified Files:
{mod_section}

Deleted Files:
{del_section}

Recently Modified Files:
{recent_section}
"""
    return summary
