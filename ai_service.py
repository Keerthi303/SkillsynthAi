"""
AI Service — Gemini API integration.

Handles all communication with Google's Gemini API for generating
career analysis reports, recommendations, and insights.
"""
import json
import logging
from flask import current_app

logger = logging.getLogger(__name__)

# Lazy-import to avoid import errors when google-generativeai is not installed
_genai = None
_model = None


def _get_model():
    """Lazily initialize the Gemini model."""
    global _genai, _model
    if _model is None:
        import google.generativeai as genai
        _genai = genai
        api_key = current_app.config.get("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in configuration.")
        genai.configure(api_key=api_key)
        model_name = current_app.config.get("GEMINI_MODEL", "gemini-2.5-flash")
        _model = genai.GenerativeModel(model_name)
    return _model


def generate_text(prompt: str, max_tokens: int = 8192) -> str:
    """Generate text from a prompt using Gemini."""
    try:
        model = _get_model()
        response = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": max_tokens, "temperature": 0.7},
        )
        return response.text
    except Exception as e:
        logger.error("Gemini API error: %s", e)
        raise


def generate_json(prompt: str, max_tokens: int = 8192) -> dict:
    """Generate structured JSON from a prompt."""
    full_prompt = (
        prompt
        + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown fences, no explanation."
    )
    try:
        text = generate_text(full_prompt, max_tokens)
        # Strip markdown fences if present
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        if text.startswith("json"):
            text = text[4:].strip()
        return json.loads(text)
    except json.JSONDecodeError:
        logger.error("Failed to parse AI response as JSON: %s", text[:500])
        return {"error": "Failed to parse AI response", "raw": text[:1000]}
    except Exception as e:
        logger.error("AI JSON generation failed: %s", e)
        return {"error": str(e)}


def generate_resume_analysis(resume_text: str, target_role: str, role_context: str = "") -> dict:
    """Generate deep resume analysis with AI."""
    prompt = f"""You are an expert career analyst and ATS specialist. Analyze the following resume for the target role of "{target_role}".

{f"INDUSTRY CONTEXT FOR THIS ROLE:{chr(10)}{role_context}{chr(10)}" if role_context else ""}

RESUME TEXT:
{resume_text}

Provide a comprehensive JSON analysis with these exact keys:
{{
    "ats_score": <integer 0-100>,
    "skills_detected": ["skill1", "skill2", ...],
    "technologies": ["tech1", "tech2", ...],
    "frameworks": ["framework1", ...],
    "tools": ["tool1", ...],
    "projects": [
        {{"name": "...", "description": "...", "technologies": ["..."]}}
    ],
    "experience_years": <estimated integer>,
    "experience_summary": "...",
    "missing_keywords": ["keyword1", "keyword2", ...],
    "formatting_issues": ["issue1", "issue2", ...],
    "strengths": ["strength1", ...],
    "weaknesses": ["weakness1", ...],
    "improvement_suggestions": ["suggestion1", ...],
    "recruiter_readiness": "high/medium/low",
    "summary": "2-3 sentence professional summary of the candidate"
}}"""
    return generate_json(prompt)


def generate_github_analysis(github_data: dict, target_role: str, role_context: str = "") -> dict:
    """Generate deep GitHub profile analysis with AI."""
    prompt = f"""You are a senior engineering manager evaluating a developer's GitHub profile for the role of "{target_role}".

{f"INDUSTRY CONTEXT:{chr(10)}{role_context}{chr(10)}" if role_context else ""}

GITHUB PROFILE DATA:
{json.dumps(github_data, indent=2)}

Provide a comprehensive JSON analysis:
{{
    "developer_profile_summary": "...",
    "primary_languages": [{{"language": "...", "percentage": <float>, "proficiency": "expert/advanced/intermediate/beginner"}}],
    "tech_stack": ["tech1", ...],
    "frameworks_detected": ["framework1", ...],
    "databases_used": ["db1", ...],
    "ai_ml_usage": true/false,
    "ai_ml_details": "...",
    "repo_quality_score": <integer 0-100>,
    "top_repos": [
        {{"name": "...", "description": "...", "quality_score": <int>, "highlights": ["..."]}}
    ],
    "commit_consistency": "high/medium/low",
    "commit_analysis": "...",
    "project_complexity": "high/medium/low",
    "readme_quality": "excellent/good/needs-improvement/poor",
    "open_source_contributions": <integer>,
    "strengths": ["..."],
    "areas_for_improvement": ["..."],
    "overall_score": <integer 0-100>
}}"""
    return generate_json(prompt)


def generate_leetcode_analysis(leetcode_data: dict, target_role: str) -> dict:
    """Generate LeetCode analysis with AI."""
    prompt = f"""You are a technical interview coach analyzing a candidate's LeetCode profile for the role of "{target_role}".

LEETCODE DATA:
{json.dumps(leetcode_data, indent=2)}

Provide a comprehensive JSON analysis:
{{
    "total_solved": <integer>,
    "easy_solved": <integer>,
    "medium_solved": <integer>,
    "hard_solved": <integer>,
    "contest_rating": <integer or null>,
    "contest_ranking": <string or null>,
    "dsa_readiness_level": "Beginner/Intermediate/Advanced",
    "dsa_readiness_score": <integer 0-100>,
    "strong_topics": ["topic1", ...],
    "weak_topics": ["topic1", ...],
    "topics_to_improve": [
        {{"topic": "...", "reason": "...", "recommended_problems": <integer>}}
    ],
    "interview_readiness": "high/medium/low",
    "strengths": ["..."],
    "recommendations": ["..."],
    "summary": "..."
}}"""
    return generate_json(prompt)


def generate_skill_gap_report(
    user_skills: list,
    role_requirements: dict,
    resume_analysis: dict,
    github_analysis: dict,
    leetcode_analysis: dict,
    target_role: str,
    role_context: str = "",
) -> dict:
    """Generate comprehensive skill gap analysis."""
    prompt = f"""You are an AI career mentor creating a skill-gap analysis for a candidate targeting the role of "{target_role}".

{f"INDUSTRY STANDARDS FOR THIS ROLE:{chr(10)}{role_context}{chr(10)}" if role_context else ""}

ROLE REQUIREMENTS:
{json.dumps(role_requirements, indent=2)}

USER'S DETECTED SKILLS: {json.dumps(user_skills)}

RESUME ANALYSIS SUMMARY:
{json.dumps(resume_analysis, indent=2)}

GITHUB ANALYSIS SUMMARY:
{json.dumps(github_analysis, indent=2)}

LEETCODE ANALYSIS SUMMARY:
{json.dumps(leetcode_analysis, indent=2)}

Generate a comprehensive skill-gap report as JSON:
{{
    "hiring_readiness_percentage": <integer 0-100>,
    "strong_skills": [{{"skill": "...", "level": "expert/advanced/intermediate", "evidence": "..."}}],
    "weak_skills": [{{"skill": "...", "current_level": "...", "required_level": "...", "gap": "..."}}],
    "missing_skills": [{{"skill": "...", "importance": "critical/important/nice-to-have", "description": "..."}}],
    "improvement_roadmap": [
        {{"phase": 1, "title": "...", "duration": "...", "tasks": ["..."], "skills_covered": ["..."]}}
    ],
    "recommended_projects": [
        {{"title": "...", "description": "...", "skills_practiced": ["..."], "difficulty": "beginner/intermediate/advanced"}}
    ],
    "coding_questions_to_practice": [
        {{"topic": "...", "questions": ["..."], "difficulty": "easy/medium/hard"}}
    ],
    "interview_preparation": {{
        "technical_topics": ["..."],
        "behavioral_topics": ["..."],
        "system_design_topics": ["..."]
    }},
    "overall_assessment": "...",
    "time_to_ready": "..."
}}"""
    return generate_json(prompt, max_tokens=12000)


def generate_resource_recommendations(weak_areas: list, missing_skills: list, target_role: str) -> dict:
    """Generate personalized learning resource recommendations."""
    prompt = f"""You are an AI career advisor. Based on the candidate's weak areas and missing skills for the role of "{target_role}", recommend the best learning resources.

WEAK AREAS: {json.dumps(weak_areas)}
MISSING SKILLS: {json.dumps(missing_skills)}

Provide personalized recommendations as JSON:
{{
    "youtube_playlists": [
        {{"title": "...", "channel": "...", "url": "https://youtube.com/...", "skill": "...", "description": "..."}}
    ],
    "github_repositories": [
        {{"name": "...", "url": "https://github.com/...", "skill": "...", "stars": "...", "description": "..."}}
    ],
    "articles_and_docs": [
        {{"title": "...", "url": "https://...", "skill": "...", "type": "article/documentation/tutorial"}}
    ],
    "dsa_sheets": [
        {{"name": "...", "url": "...", "problems_count": <int>, "description": "..."}}
    ],
    "interview_resources": [
        {{"title": "...", "url": "...", "type": "questions/guide/mock", "description": "..."}}
    ],
    "courses": [
        {{"title": "...", "platform": "...", "url": "...", "skill": "...", "free": true/false}}
    ]
}}

IMPORTANT: Use REAL, well-known resources. Do NOT make up URLs — use actual popular resources from the tech community."""
    return generate_json(prompt)
