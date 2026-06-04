import os
import sys
import json
try:
    import requests
except ImportError:
    print(
        "Missing dependency: requests. Install with 'pip install requests'", file=sys.stderr
    )
    sys.exit(1)
from datetime import datetime

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = "6b97861b-550e-8389-ae4a-01f29a260f79"

# Validate required environment variables early and provide a clear message
missing = []
if not NOTION_TOKEN:
    missing.append("NOTION_TOKEN")
if not DATABASE_ID:
    missing.append("DATABASE_ID")
if missing:
    print(
        "Missing required environment variables: " + ", ".join(missing),
        file=sys.stderr,
    )
    print(
        "Set them in your GitHub Actions workflow or repository secrets.",
        file=sys.stderr,
    )
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def fetch_all_pages():
    """Fetch all pages from the Notion database (handles pagination)."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    all_results = []
    payload = {}

    while True:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()

        all_results.extend(data.get("results", []))

        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]

    return all_results


def parse_property(prop):
    """Parse a single Notion property into a plain Python value."""
    prop_type = prop.get("type")

    if prop_type == "title":
        parts = prop["title"]
        return "".join(p.get("plain_text", "") for p in parts)

    elif prop_type == "rich_text":
        parts = prop["rich_text"]
        return "".join(p.get("plain_text", "") for p in parts)

    elif prop_type == "number":
        return prop.get("number")

    elif prop_type == "select":
        sel = prop.get("select")
        return sel["name"] if sel else None

    elif prop_type == "multi_select":
        return [s["name"] for s in prop.get("multi_select", [])]

    elif prop_type == "status":
        status = prop.get("status")
        return status["name"] if status else None

    elif prop_type == "date":
        date = prop.get("date")
        if date:
            return {"start": date.get("start"), "end": date.get("end")}
        return None

    elif prop_type == "checkbox":
        return prop.get("checkbox")

    elif prop_type == "url":
        return prop.get("url")

    elif prop_type == "email":
        return prop.get("email")

    elif prop_type == "phone_number":
        return prop.get("phone_number")

    elif prop_type == "formula":
        formula = prop.get("formula", {})
        f_type = formula.get("type")
        return formula.get(f_type)

    elif prop_type == "relation":
        return [r["id"] for r in prop.get("relation", [])]

    elif prop_type == "people":
        return [
            p.get("name") or p.get("id")
            for p in prop.get("people", [])
        ]

    elif prop_type == "files":
        files = []
        for f in prop.get("files", []):
            if f.get("type") == "external":
                files.append(f["external"]["url"])
            elif f.get("type") == "file":
                files.append(f["file"]["url"])
        return files

    elif prop_type == "created_time":
        return prop.get("created_time")

    elif prop_type == "last_edited_time":
        return prop.get("last_edited_time")

    else:
        # Fallback: return raw value
        return prop.get(prop_type)


def transform_pages(pages):
    """Transform raw Notion pages into clean flat records."""
    records = []
    for page in pages:
        record = {
            "id": page["id"],
            "created_time": page.get("created_time"),
            "last_edited_time": page.get("last_edited_time"),
            "url": page.get("url"),
        }
        for prop_name, prop_value in page.get("properties", {}).items():
            record[prop_name] = parse_property(prop_value)
        records.append(record)
    return records


def main():
    print(f"[{datetime.utcnow().isoformat()}] Fetching Notion database...")

    pages = fetch_all_pages()
    print(f"  Found {len(pages)} pages.")

    records = transform_pages(pages)

    output = {
        "last_synced": datetime.utcnow().isoformat() + "Z",
        "total": len(records),
        "items": records,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/notion_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"  Saved to data/notion_data.json")
    print(f"[{datetime.utcnow().isoformat()}] Done.")


if __name__ == "__main__":
    main()
