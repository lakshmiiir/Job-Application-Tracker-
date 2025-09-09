Job Application Tracker (SQLite + Notion Integration)

This project is a Python automation tool that streamlines job application tracking. It stores applications in a local SQLite database and automatically creates corresponding entries in a Notion database via the Notion API.

✨ Features

SQLite persistence: All job applications are stored locally with details such as company, role, location, deadlines, and notes.

Notion integration: Syncs new applications directly into a Notion database for easy visualization.

Interactive input or pre-defined entries: Add jobs manually through prompts or as hardcoded dictionaries.

Data validation: Ensures only valid statuses and application states are passed into Notion.

Automation-friendly: Can be extended for batch imports or integrated into your workflow.

🛠️ Technologies

Python 3

SQLite

Requests (HTTP library)

Notion API
