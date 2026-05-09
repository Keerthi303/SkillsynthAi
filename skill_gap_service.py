"""
Skill Gap Service — Compare user skills against role requirements.
"""
import logging

logger = logging.getLogger(__name__)


def compute_skill_gap(user_skills: list, role_data: dict) -> dict:
    """Compare user skills against role requirements and compute gap analysis."""
    if not role_data:
        return {"error": "No role data available"}

    required = [s.lower() for s in role_data.get("required_skills", [])]
    user_lower = [s.lower() for s in user_skills]

    strong = [s for s in required if s in user_lower]
    missing = [s for s in required if s not in user_lower]
    extra = [s for s in user_lower if s not in required]

    coverage = len(strong) / max(len(required), 1) * 100
    hiring_readiness = min(int(coverage * 0.8 + len(extra) * 0.5), 100)

    return {
        "role": role_data.get("role", "Unknown"),
        "required_skills": role_data.get("required_skills", []),
        "strong_skills": strong,
        "missing_skills": missing,
        "extra_skills": extra,
        "coverage_percentage": round(coverage, 1),
        "hiring_readiness": hiring_readiness,
        "interview_topics": role_data.get("interview_topics", []),
        "hiring_expectations": role_data.get("hiring_expectations", {}),
        "industry_standards": role_data.get("industry_standards", []),
    }
