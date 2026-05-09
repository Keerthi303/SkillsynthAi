"""
Configuration management for Skill Synth AI.

Loads settings from environment variables (via .env in dev) and exposes
config classes per environment. The app factory picks one based on FLASK_ENV.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Project root — used for resolving paths consistently
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if present
load_dotenv(BASE_DIR / ".env")


class BaseConfig:
    """Settings shared across all environments."""

    # --- Flask ---
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-insecure-key-change-me")

    # --- Database ---
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Uploads ---
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10")) * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf", "docx"}

    # --- AI Provider (Gemini) ---
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # --- External APIs ---
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

    # --- ChromaDB ---
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chromadb"))

    # --- Paths ---
    BASE_DIR = BASE_DIR


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    # Hard-fail in prod if SECRET_KEY isn't set properly
    @classmethod
    def init_app(cls, app):
        if cls.SECRET_KEY == "dev-only-insecure-key-change-me":
            raise RuntimeError("SECRET_KEY must be set in production!")


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Return the config class matching FLASK_ENV, defaulting to development."""
    env = os.getenv("FLASK_ENV", "development").lower()
    return config_map.get(env, DevelopmentConfig)
