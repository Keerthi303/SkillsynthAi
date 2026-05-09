"""
Report Service — Generate and export analysis reports.
"""
import io
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_full_report(resume_analysis, github_analysis, leetcode_analysis, skill_gap, ai_report, resources, target_role):
    """Combine all analyses into a single comprehensive report."""
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "target_role": target_role,
        "resume_analysis": resume_analysis,
        "github_analysis": github_analysis,
        "leetcode_analysis": leetcode_analysis,
        "skill_gap": skill_gap,
        "ai_report": ai_report,
        "resources": resources,
        "summary": {
            "ats_score": resume_analysis.get("ats_score", 0) if isinstance(resume_analysis, dict) else 0,
            "hiring_readiness": ai_report.get("hiring_readiness_percentage", skill_gap.get("hiring_readiness", 0)) if isinstance(ai_report, dict) else 0,
            "dsa_level": leetcode_analysis.get("dsa_readiness_level", "N/A") if isinstance(leetcode_analysis, dict) else "N/A",
            "github_score": github_analysis.get("overall_score", 0) if isinstance(github_analysis, dict) and "overall_score" in github_analysis else 0,
        },
    }


def export_report_pdf(report_data: dict) -> bytes:
    """Generate a PDF from the report data using reportlab."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("ReportTitle", parent=styles["Title"], fontSize=22, textColor=colors.HexColor("#1a1a2e"), spaceAfter=6)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=11, textColor=colors.HexColor("#666"), spaceAfter=20)
    heading_style = ParagraphStyle("SectionHead", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#1a1a2e"), spaceBefore=20, spaceAfter=10)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=14)
    accent = colors.HexColor("#0ea5e9")

    elements = []

    # Title
    elements.append(Paragraph("Skill Synth AI — Career Analysis Report", title_style))
    elements.append(Paragraph(f"Target Role: {report_data.get('target_role', 'N/A')} | Generated: {report_data.get('generated_at', '')[:10]}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=accent, spaceAfter=20))

    # Summary scores
    summary = report_data.get("summary", {})
    summary_data = [
        ["Metric", "Score"],
        ["ATS Score", f"{summary.get('ats_score', 0)}%"],
        ["Hiring Readiness", f"{summary.get('hiring_readiness', 0)}%"],
        ["DSA Level", summary.get("dsa_level", "N/A")],
        ["GitHub Score", f"{summary.get('github_score', 0)}/100"],
    ]
    t = Table(summary_data, colWidths=[3*inch, 2*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), accent),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # AI Report sections
    ai = report_data.get("ai_report", {})
    if isinstance(ai, dict):
        # Strong Skills
        strong = ai.get("strong_skills", [])
        if strong:
            elements.append(Paragraph("Strong Skills", heading_style))
            for s in strong[:10]:
                if isinstance(s, dict):
                    elements.append(Paragraph(f"• <b>{s.get('skill','')}</b> — {s.get('evidence','')}", body_style))
                else:
                    elements.append(Paragraph(f"• {s}", body_style))
            elements.append(Spacer(1, 10))

        # Missing Skills
        missing = ai.get("missing_skills", [])
        if missing:
            elements.append(Paragraph("Missing Skills", heading_style))
            for s in missing[:10]:
                if isinstance(s, dict):
                    elements.append(Paragraph(f"• <b>{s.get('skill','')}</b> ({s.get('importance','')}) — {s.get('description','')}", body_style))
                else:
                    elements.append(Paragraph(f"• {s}", body_style))
            elements.append(Spacer(1, 10))

        # Roadmap
        roadmap = ai.get("improvement_roadmap", [])
        if roadmap:
            elements.append(Paragraph("Improvement Roadmap", heading_style))
            for phase in roadmap[:5]:
                if isinstance(phase, dict):
                    elements.append(Paragraph(f"<b>Phase {phase.get('phase','')}:</b> {phase.get('title','')} ({phase.get('duration','')})", body_style))
                    for task in phase.get("tasks", [])[:5]:
                        elements.append(Paragraph(f"    → {task}", body_style))
            elements.append(Spacer(1, 10))

        # Assessment
        assessment = ai.get("overall_assessment", "")
        if assessment:
            elements.append(Paragraph("Overall Assessment", heading_style))
            elements.append(Paragraph(assessment, body_style))

    # Footer
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#ccc")))
    elements.append(Paragraph("Generated by Skill Synth AI — Your AI Career Mentor", ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#999"), alignment=1)))

    doc.build(elements)
    return buffer.getvalue()
