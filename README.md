# EchoSpace – Anonymous Emotion Sharing & Support Platform

EchoSpace is a student-friendly web technology project for anonymous community notes and personal mood reflection. It is built with **Python, Streamlit, SQLite, Pandas, and Plotly**.

## Features
- Anonymous community posts with basic contact/link screening
- Supportive reactions and a report-note workflow
- Mood journal with tags and optional reflections
- Mood trend and distribution charts
- CSV export for personal mood entries
- Community guidelines and privacy/safety notices
- Local SQLite persistence; no account required

## Project structure
```text
EchoSpace/
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Run locally
1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Create and activate a virtual environment (recommended):
   - Windows: `py -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   streamlit run app.py
   ```
6. Open the local URL Streamlit prints in your terminal.

## GitHub upload
Upload `app.py`, `database.py`, `requirements.txt`, `.gitignore`, and `README.md`.
Do **not** upload `.venv/`, `__pycache__/`, or `echospace.db` (the database is created automatically when the app runs).

## Important privacy note
This is an educational prototype, not a clinical or crisis service. The local SQLite database is not encrypted. If hosted publicly, posts would be visible to other visitors and mood entries may be accessible to the server operator. Do not use it for real sensitive disclosures without authentication/authorization boundaries, stronger moderation, encryption where appropriate, retention controls, and a reviewed privacy policy. Anonymity cannot be guaranteed against a host or administrator.

## Suggested future enhancements
- Moderator dashboard for reviewing reports
- Rate limiting and anti-spam controls
- Better personal-data detection
- Automated tests
- Deployment configuration and a formal privacy/consent flow
