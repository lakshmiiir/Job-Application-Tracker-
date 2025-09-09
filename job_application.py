import os
import sqlite3
import requests
import datetime

# ============ CONFIG ============
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID    = os.environ.get("NOTION_DATABASE_ID")


DB_PATH = "/Users/lakshmiramesh/Downloads/Job Application Tracker/dbs/job_application.db"


HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Allowed values based on your schema
ALLOWED_STATUS = {"Not started", "In progress", "Done"}
ALLOWED_APP_STATUS = {"Accepted", "Rejected", "Interview", "No Response Yet"}

# ============ DB ============
def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        print("SQLite file:", conn.execute("PRAGMA database_list;").fetchall())
        cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            industry TEXT,
            status TEXT,
            application_status TEXT,
            company_name TEXT,
            job_title TEXT,
            location TEXT,
            link TEXT,
            referral INTEGER,
            deadline TEXT,
            applied_date TEXT,
            notes TEXT
        );
        """)
        conn.commit()
    finally:
        conn.close()

def add_to_db(industry, status, app_status, company, title, location,
              link, referral, deadline, applied_date, notes):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO applications
            (industry, status, application_status, company_name, job_title, location,
             link, referral, deadline, applied_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (industry, status, app_status, company, title, location,
              link, referral, deadline, applied_date, notes))
        conn.commit()
        row_id = cur.lastrowid
        print(f"SQLite insert OK — row id: {row_id}")
        return row_id
    finally:
        conn.close()

# ============ NOTION ============
def add_to_notion(industry, status, app_status, company, title, location,
                  link, referral, deadline, applied_date, notes):
    # Validate against allowed values
    if status not in ALLOWED_STATUS:
        raise ValueError(f"Status must be one of {sorted(ALLOWED_STATUS)}")
    if app_status not in ALLOWED_APP_STATUS:
        raise ValueError(f"Application Status must be one of {sorted(ALLOWED_APP_STATUS)}")

    # Build properties dynamically
    properties = {
        # IMPORTANT: This must be your database's "Title" property
        "🫧 Industry ": {"title": [{"text": {"content": industry}}]},
        "🫧 Status": {"status": {"name": status}},
        "🫧 Application Status": {"select": {"name": app_status}},
    }

    if company:
        properties["🫧 Company Name "] = {"rich_text": [{"text": {"content": company}}]}
    if title:
        properties["🫧 Job Title"] = {"rich_text": [{"text": {"content": title}}]}
    if location:
        properties["🫧 Location"] = {"rich_text": [{"text": {"content": location}}]}
    if link:
        properties["🫧 Link"] = {"url": link}
    if referral is not None:
        properties["🫧 Referral"] = {"checkbox": bool(referral)}
    if deadline:
        properties["🫧 Deadline"] = {"date": {"start": deadline}}
    if applied_date:
        properties["🫧 Applied Date"] = {"date": {"start": applied_date}}
    if notes:
        properties["🫧 Notes "] = {"rich_text": [{"text": {"content": notes}}]}

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": properties
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=payload)
    if res.status_code not in (200, 201):
        print("Notion error:", res.status_code, res.text)
        return None

    data = res.json()
    page_url = data.get("url")
    print("Notion page created:", page_url)
    return page_url

# ============ RUN ONCE ============
if __name__ == "__main__":
    init_db()

    job = {
        "industry": "Engineering & Consulting",
        "status": "Not started",
        "app_status": "No Response Yet",
        "company": "Hatch",
        "title": "New Graduate - Advisory Business Analyst",
        "location": "Brooklyn, NY",
        "link": "https://jobs.hatch.com/job/Brooklyn-New-Graduate-Advisory-Business-Analyst-NY/1323354000/?utm_source=LINKEDIN&utm_medium=referrer",
        "referral": 0, #1 =yes 0 =no 
        "deadline": "",
        "applied_date": datetime.date.today().isoformat(),
        "notes": ""
    }

    add_to_db(**job)
    add_to_notion(**job)
