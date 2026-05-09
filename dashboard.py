"""
Dashboard routes — main app interface after login.
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard_page():
    reports = current_user.reports.limit(10).all()
    return render_template("dashboard/index.html", reports=reports)


@dashboard_bp.route("/dashboard/analyze")
@login_required
def analyze_page():
    return render_template("dashboard/analyze.html")


@dashboard_bp.route("/dashboard/report/<int:report_id>")
@login_required
def report_page(report_id):
    from backend.models.report import Report
    report = Report.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    return render_template("dashboard/report.html", report=report)


@dashboard_bp.route("/dashboard/history")
@login_required
def history_page():
    reports = current_user.reports.all()
    return render_template("dashboard/history.html", reports=reports)
