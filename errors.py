"""
Application-wide error handlers.
"""
from flask import render_template, jsonify, request


def register_error_handlers(app):
    """Attach error handlers to the Flask app."""

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/"):
            return jsonify(error="not_found", message=str(e)), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def too_large(e):
        msg = "Uploaded file is too large."
        if request.path.startswith("/api/"):
            return jsonify(error="payload_too_large", message=msg), 413
        return render_template("errors/500.html", message=msg), 413

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception("Internal server error")
        if request.path.startswith("/api/"):
            return jsonify(error="server_error", message="Something went wrong."), 500
        return render_template("errors/500.html"), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Catch-all for unexpected errors on API routes."""
        if request.path.startswith("/api/"):
            app.logger.exception("Unhandled API exception")
            return jsonify(error="exception", message=str(e)), 500
        raise e
