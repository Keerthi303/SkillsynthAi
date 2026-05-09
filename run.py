"""
Entry point for Skill Synth AI.

Run locally:
    python run.py

Run in production (example):
    gunicorn -w 4 'run:app'
"""
from backend import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=app.config.get("DEBUG", False))
