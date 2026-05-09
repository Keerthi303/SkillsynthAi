"""
Flask extension instances.

Defined here so any module can import them without triggering the
app factory, avoiding circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
