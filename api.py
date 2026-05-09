"""
Analysis API routes — resume upload, GitHub/LeetCode analysis, full report generation.
"""
import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from backend.extensions import db

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")

ALLOWED_EXT = {"pdf", "docx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@api_bp.route("/roles", methods=["GET"])
def get_roles():
    from backend.services.rag_service import get_all_roles
    return jsonify({"roles": get_all_roles()})


@api_bp.route("/analyze", methods=["POST"])
@login_required
def run_analysis():
    """Run full career analysis pipeline."""
    # 1. Collect inputs
    target_role = request.form.get("target_role", "").strip()
    github_url = request.form.get("github_url", "").strip()
    leetcode_username = request.form.get("leetcode_username", "").strip()
    resume_file = request.files.get("resume")

    if not target_role:
        return jsonify({"error": "Target role is required"}), 400

    results = {"target_role": target_role, "errors": []}

    # 2. Resume Analysis
    resume_analysis = {}
    resume_text = ""
    if resume_file and allowed_file(resume_file.filename):
        try:
            filename = secure_filename(f"{current_user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{resume_file.filename}")
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            resume_file.save(filepath)

            from backend.services.resume_service import analyze_resume
            resume_analysis = analyze_resume(filepath, target_role)
            resume_text = resume_analysis.get("text", "")
            results["resume_analysis"] = {k: v for k, v in resume_analysis.items() if k != "text"}
        except Exception as e:
            logger.error("Resume analysis error: %s", e)
            results["errors"].append(f"Resume analysis failed: {str(e)}")
    elif resume_file:
        results["errors"].append("Invalid file type. Only PDF and DOCX are accepted.")

    # 3. GitHub Analysis
    github_data = {}
    if github_url:
        try:
            from backend.services.github_service import analyze_github
            github_data = analyze_github(github_url)
            if "error" not in github_data:
                results["github_analysis"] = github_data
            else:
                results["errors"].append(github_data["error"])
        except Exception as e:
            logger.error("GitHub analysis error: %s", e)
            results["errors"].append(f"GitHub analysis failed: {str(e)}")

    # 4. LeetCode Analysis
    leetcode_data = {}
    if leetcode_username:
        try:
            from backend.services.leetcode_service import analyze_leetcode
            leetcode_data = analyze_leetcode(leetcode_username)
            if "error" not in leetcode_data:
                results["leetcode_analysis"] = leetcode_data
            else:
                results["errors"].append(leetcode_data["error"])
        except Exception as e:
            logger.error("LeetCode analysis error: %s", e)
            results["errors"].append(f"LeetCode analysis failed: {str(e)}")

    # 5. RAG — retrieve role context
    from backend.services.rag_service import query_role
    rag_result = query_role(target_role)
    role_context = rag_result.get("context", "")
    role_data = rag_result.get("role_data")
    results["rag_match"] = {"found": rag_result["found"], "matched_role": rag_result.get("matched_role", "")}

    # 6. Skill Gap (basic computation)
    user_skills = resume_analysis.get("skills_detected", [])
    if github_data and "languages" in github_data:
        user_skills += list(github_data["languages"].keys())
    if github_data and "frameworks" in github_data:
        user_skills += github_data["frameworks"]
    user_skills = list(set(s.lower() for s in user_skills))

    if role_data:
        from backend.services.skill_gap_service import compute_skill_gap
        skill_gap = compute_skill_gap(user_skills, role_data)
        results["skill_gap"] = skill_gap
    else:
        skill_gap = {}

    # 7. AI-powered deep analysis
    try:
        from backend.services.ai_service import (
            generate_resume_analysis, generate_github_analysis,
            generate_leetcode_analysis, generate_skill_gap_report,
            generate_resource_recommendations
        )

        ai_resume = {}
        if resume_text:
            ai_resume = generate_resume_analysis(resume_text, target_role, role_context)
            results["ai_resume_analysis"] = ai_resume

        ai_github = {}
        if github_data and "error" not in github_data:
            ai_github = generate_github_analysis(github_data, target_role, role_context)
            results["ai_github_analysis"] = ai_github

        ai_leetcode = {}
        if leetcode_data and "error" not in leetcode_data:
            ai_leetcode = generate_leetcode_analysis(leetcode_data, target_role)
            results["ai_leetcode_analysis"] = ai_leetcode

        # Full skill gap report
        ai_report = generate_skill_gap_report(user_skills, role_data or {}, ai_resume, ai_github, ai_leetcode, target_role, role_context)
        results["ai_report"] = ai_report

        # Resources
        weak_areas = ai_report.get("weak_skills", [])
        missing = ai_report.get("missing_skills", [])
        weak_names = [w.get("skill", w) if isinstance(w, dict) else w for w in weak_areas]
        missing_names = [m.get("skill", m) if isinstance(m, dict) else m for m in missing]
        resources = generate_resource_recommendations(weak_names, missing_names, target_role)
        results["resources"] = resources

    except Exception as e:
        logger.error("AI analysis error: %s", e)
        results["errors"].append(f"AI analysis encountered an error: {str(e)}")
        results["ai_report"] = {}
        results["resources"] = {}

    # 8. Save report to DB
    try:
        from backend.models.report import Report
        from backend.services.report_service import generate_full_report

        full_report = generate_full_report(
            results.get("resume_analysis", results.get("ai_resume_analysis", {})),
            results.get("ai_github_analysis", results.get("github_analysis", {})),
            results.get("ai_leetcode_analysis", results.get("leetcode_analysis", {})),
            skill_gap, results.get("ai_report", {}), results.get("resources", {}), target_role
        )

        report = Report(
            user_id=current_user.id,
            target_role=target_role,
            ats_score=full_report["summary"]["ats_score"],
            hiring_readiness=full_report["summary"]["hiring_readiness"],
            dsa_level=full_report["summary"]["dsa_level"],
        )
        report.set_data(full_report)
        db.session.add(report)
        db.session.commit()
        results["report_id"] = report.id
    except Exception as e:
        logger.error("Report save error: %s", e)
        results["errors"].append(f"Failed to save report: {str(e)}")

    return jsonify(results)


@api_bp.route("/report/<int:report_id>", methods=["GET"])
@login_required
def get_report(report_id):
    from backend.models.report import Report
    report = Report.query.filter_by(id=report_id, user_id=current_user.id).first()
    if not report:
        return jsonify({"error": "Report not found"}), 404
    return jsonify({"report": report.to_dict(), "data": report.get_data()})


@api_bp.route("/report/<int:report_id>/pdf", methods=["GET"])
@login_required
def export_pdf(report_id):
    from backend.models.report import Report
    from backend.services.report_service import export_report_pdf
    import io

    report = Report.query.filter_by(id=report_id, user_id=current_user.id).first()
    if not report:
        return jsonify({"error": "Report not found"}), 404

    pdf_bytes = export_report_pdf(report.get_data())
    return send_file(io.BytesIO(pdf_bytes), mimetype="application/pdf", as_attachment=True, download_name=f"skill_synth_report_{report_id}.pdf")


@api_bp.route("/reports", methods=["GET"])
@login_required
def list_reports():
    from backend.models.report import Report
    reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
    return jsonify({"reports": [r.to_dict() for r in reports]})


@api_bp.route("/report/<int:report_id>", methods=["DELETE"])
@login_required
def delete_report(report_id):
    from backend.models.report import Report
    report = Report.query.filter_by(id=report_id, user_id=current_user.id).first()
    if not report:
        return jsonify({"error": "Report not found"}), 404
    db.session.delete(report)
    db.session.commit()
    return jsonify({"success": True})
