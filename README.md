# Notion → GitHub Sync

Automatically syncs a Notion database to `data/notion_data.json` every day at midnight UTC via GitHub Actions.

---

## Setup

### 1. Create a Notion Integration

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click **"+ New integration"**
3. Give it a name (e.g. `github-sync`), select your workspace
4. Copy the **Internal Integration Token** — this is your `NOTION_TOKEN`

### 2. Share Your Database with the Integration

1. Open your Notion database
2. Click **"..." (3 dots)** → **"Add connections"**
3. Search for and select the integration you just created

### 3. Get Your Database ID

Your database URL looks like:
```
https://www.notion.so/yourworkspace/THIS_IS_THE_DATABASE_ID?v=...
```
Copy the part between the last `/` and the `?` — that's your `NOTION_DATABASE_ID`.

### 4. Add Secrets to GitHub

In your GitHub repo, go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret Name           | Value                          |
|-----------------------|--------------------------------|
| `NOTION_TOKEN`        | Your Notion integration token  |
| `NOTION_DATABASE_ID`  | Your Notion database ID        |

### 5. Push These Files to Your Repo

Make sure these files exist in your repo:
```
.github/
  workflows/
    sync_notion.yml
scripts/
  fetch_notion.py
data/
  notion_data.json    ← placeholder, will be overwritten on first sync
```

---

## Output Format

`data/notion_data.json` will look like:

```json
{
  "last_synced": "2024-06-04T00:00:00Z",
  "total": 42,
  "items": [
    {
      "id": "page-id",
      "created_time": "2024-01-01T00:00:00.000Z",
      "last_edited_time": "2024-06-01T00:00:00.000Z",
      "url": "https://notion.so/...",
      "Name": "My Tool",
      "Status": "Exploring",
      "Tags": ["AI", "Productivity"],
      "Description": "A short description..."
    }
  ]
}
```

All your Notion columns are automatically parsed — titles, selects, multi-selects, checkboxes, dates, URLs, etc.

---

## Manual Trigger

You can trigger the sync anytime from **GitHub → Actions → Sync Notion Database → Run workflow**.

---

## Schedule

Runs daily at **00:00 UTC**. To change the schedule, edit the `cron` value in `.github/workflows/sync_notion.yml`.
