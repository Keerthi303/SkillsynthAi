"""
Centralized logging setup.
"""
import logging
import sys


def setup_logging(app):
    """Configure logging for the Flask app."""
    level = logging.DEBUG if app.config.get("DEBUG") else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    # Configure both Flask logger and root
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(level)

    # Quieten noisy third-party loggers
    for noisy in ("werkzeug", "chromadb", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
