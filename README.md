# Skill Synth AI — AI-Powered Career Analysis Platform

A full-stack AI career analysis platform that analyzes your **Resume**, **GitHub** profile, and **LeetCode** profile to generate a comprehensive skill-gap report with personalized improvement resources.

## Features

- **Resume Analysis** — PDF/DOCX parsing, skill extraction, ATS scoring, formatting audit
- **GitHub Analysis** — Language breakdown, repo quality, framework detection, commit consistency
- **LeetCode Analysis** — Problem stats, DSA readiness level, topic-wise strengths/weaknesses
- **Skill Gap Engine** — Compare your skills against industry-standard role requirements
- **RAG Pipeline** — ChromaDB knowledge base with 10 pre-built role profiles
- **AI Reports** — Deep, personalized career analysis via Google Gemini
- **Resource Recommendations** — YouTube, GitHub repos, articles, courses matched to your gaps
- **PDF Export** — Professional report generation with ReportLab
- **Auth System** — User registration, login, session management
- **Admin Panel** — Manage roles, users, reports, knowledge base
- **Report History** — Save and review past analyses

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Backend | Python Flask |
| Database | SQLite (user data) + ChromaDB (RAG vectors) |
| AI | Google Gemini API |
| PDF | ReportLab |

## Project Structure

```
skill-synth-ai/
├── backend/
│   ├── __init__.py          # App factory
│   ├── extensions.py        # Flask extensions
│   ├── errors.py            # Error handlers
│   ├── models/
│   │   ├── user.py          # User model
│   │   └── report.py        # Report model
│   ├── routes/
│   │   ├── main.py          # Landing page
│   │   ├── auth.py          # Authentication
│   │   ├── dashboard.py     # Dashboard pages
│   │   ├── api.py           # Analysis API
│   │   └── admin.py         # Admin panel
│   ├── services/
│   │   ├── ai_service.py    # Gemini API integration
│   │   ├── rag_service.py   # ChromaDB + knowledge base
│   │   ├── resume_service.py # Resume parsing
│   │   ├── github_service.py # GitHub API
│   │   ├── leetcode_service.py # LeetCode API
│   │   ├── skill_gap_service.py # Skill comparison
│   │   └── report_service.py   # Report generation
│   └── utils/
│       └── logger.py        # Logging setup
├── templates/               # Jinja2 templates
│   ├── base.html
│   ├── index.html           # Landing page
│   ├── auth/                # Login/Register
│   ├── dashboard/           # Dashboard, Analyze, Report, History
│   ├── admin/               # Admin panel
│   └── errors/              # 404, 500
├── static/
│   ├── css/
│   │   ├── main.css         # Design system
│   │   └── app.css          # Page-level styles
│   └── js/
│       ├── main.js          # Scroll animations
│       ├── analyze.js       # Analysis form
│       ├── report.js        # Report rendering
│       └── admin.js         # Admin panel
├── uploads/                 # Resume uploads
├── chromadb/                # ChromaDB persistence
├── config.py                # Configuration
├── run.py                   # Entry point
├── requirements.txt
└── .env.example
```

## Setup Guide

### 1. Clone & Navigate
```bash
cd skill-synth-ai
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 5. Get a Gemini API Key
- Visit https://aistudio.google.com/app/apikey
- Create a free API key
- Add it to your `.env` file

### 6. Run the Application
```bash
python run.py
```

### 7. Open in Browser
Visit `http://127.0.0.1:5000`

### 8. Create Admin User (Optional)
```python
python -c "
from run import app
from backend.extensions import db
from backend.models.user import User
with app.app_context():
    u = User(name='Admin', email='admin@example.com', is_admin=True)
    u.set_password('admin123')
    db.session.add(u)
    db.session.commit()
    print('Admin user created!')
"
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/roles` | List all available roles |
| POST | `/api/analyze` | Run full analysis (multipart form) |
| GET | `/api/report/<id>` | Get report data |
| GET | `/api/report/<id>/pdf` | Export report as PDF |
| GET | `/api/reports` | List user's reports |
| DELETE | `/api/report/<id>` | Delete a report |

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `SECRET_KEY` | Flask secret key | Yes (prod) |
| `GITHUB_TOKEN` | GitHub PAT for higher rate limits | Optional |
| `FLASK_ENV` | `development` or `production` | Optional |

## License

MIT
