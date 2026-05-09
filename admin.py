"""
Admin routes — manage roles, RAG documents, view reports, analytics.
"""
import json
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from functools import wraps

from backend.extensions import db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@admin_required
def admin_panel():
    return render_template("admin/index.html")


@admin_bp.route("/api/stats")
@admin_required
def admin_stats():
    from backend.models.user import User
    from backend.models.report import Report
    from backend.services.rag_service import get_kb_stats

    return jsonify({
        "users": User.query.count(),
        "reports": Report.query.count(),
        "kb_stats": get_kb_stats(),
    })


@admin_bp.route("/api/roles", methods=["GET"])
@admin_required
def admin_roles():
    from backend.services.rag_service import get_all_roles
    return jsonify({"roles": get_all_roles()})


@admin_bp.route("/api/roles/<role_key>", methods=["GET"])
@admin_required
def admin_role_detail(role_key):
    from backend.services.rag_service import get_role_details
    details = get_role_details(role_key)
    if not details:
        return jsonify({"error": "Role not found"}), 404
    return jsonify({"role": details})


@admin_bp.route("/api/roles", methods=["POST"])
@admin_required
def admin_add_role():
    data = request.get_json(silent=True) or {}
    role_key = data.get("key", "").strip().lower().replace(" ", "_")
    if not role_key or not data.get("role"):
        return jsonify({"error": "Role key and name are required"}), 400
    from backend.services.rag_service import add_role
    add_role(role_key, data)
    return jsonify({"success": True})


@admin_bp.route("/api/reports", methods=["GET"])
@admin_required
def admin_reports():
    from backend.models.report import Report
    reports = Report.query.order_by(Report.created_at.desc()).limit(50).all()
    result = []
    for r in reports:
        d = r.to_dict()
        d["user_email"] = r.user.email if r.user else "unknown"
        result.append(d)
    return jsonify({"reports": result})


@admin_bp.route("/api/users", methods=["GET"])
@admin_required
def admin_users():
    from backend.models.user import User
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({"users": [{"id": u.id, "name": u.name, "email": u.email, "is_admin": u.is_admin, "created_at": u.created_at.isoformat() if u.created_at else None, "reports_count": u.reports.count()} for u in users]})


@admin_bp.route("/api/seed-kb", methods=["POST"])
@admin_required
def admin_seed_kb():
    from backend.services.rag_service import seed_knowledge_base
    count = seed_knowledge_base()
    return jsonify({"success": True, "documents_count": count})
