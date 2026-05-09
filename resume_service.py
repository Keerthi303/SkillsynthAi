"""
Resume Service — Extract and analyze resume content.
"""
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

COMMON_SKILLS = [
    "python","java","javascript","typescript","c++","c#","go","rust","ruby","php","swift","kotlin",
    "react","angular","vue","next.js","nuxt","svelte","django","flask","fastapi","spring","express",
    "node.js","html","css","sass","tailwind","bootstrap","jquery",
    "sql","mysql","postgresql","mongodb","redis","elasticsearch","dynamodb","cassandra","firebase",
    "docker","kubernetes","aws","gcp","azure","terraform","ansible","jenkins","github actions","ci/cd",
    "git","linux","bash","nginx","apache",
    "tensorflow","pytorch","scikit-learn","pandas","numpy","opencv","nltk","spacy","keras",
    "rest api","graphql","grpc","websocket","microservices","serverless",
    "agile","scrum","jira","confluence","figma","postman",
    "machine learning","deep learning","nlp","computer vision","data science",
    "blockchain","web3","solidity","ethereum",
]


def extract_text_from_pdf(filepath: str) -> str:
    import pdfplumber
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_from_docx(filepath: str) -> str:
    from docx import Document
    doc = Document(filepath)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext == ".docx":
        return extract_text_from_docx(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def detect_skills(text: str) -> list:
    text_lower = text.lower()
    found = []
    for skill in COMMON_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)
    return found


def detect_sections(text: str) -> dict:
    sections = {"education": False, "experience": False, "skills": False, "projects": False, "certifications": False, "summary": False, "contact": False}
    text_lower = text.lower()
    section_keywords = {
        "education": ["education","university","degree","bachelor","master","phd","gpa"],
        "experience": ["experience","work experience","employment","intern"],
        "skills": ["skills","technical skills","technologies","competencies"],
        "projects": ["projects","personal projects","academic projects"],
        "certifications": ["certifications","certificates","certified"],
        "summary": ["summary","objective","about me","profile"],
        "contact": ["email","phone","linkedin","github","address"],
    }
    for section, keywords in section_keywords.items():
        for kw in keywords:
            if kw in text_lower:
                sections[section] = True
                break
    return sections


def basic_ats_check(text: str, skills: list) -> dict:
    word_count = len(text.split())
    sections = detect_sections(text)
    section_score = sum(1 for v in sections.values() if v)
    has_contact = sections["contact"]
    has_experience = sections["experience"]
    skill_count = len(skills)

    score = 0
    issues = []
    suggestions = []

    # Word count scoring
    if 300 <= word_count <= 1000:
        score += 20
    elif word_count < 300:
        score += 5
        issues.append("Resume is too short")
        suggestions.append("Add more details about your experience and projects")
    else:
        score += 15
        issues.append("Resume may be too long for ATS")

    # Sections scoring
    score += min(section_score * 5, 25)
    if not has_contact:
        issues.append("Missing contact information section")
    if not has_experience:
        issues.append("Missing work experience section")
        suggestions.append("Add a work experience or internship section")

    # Skills scoring
    if skill_count >= 10:
        score += 25
    elif skill_count >= 5:
        score += 15
    else:
        score += 5
        suggestions.append("Add more technical skills to your resume")

    # Formatting checks
    if re.search(r'[A-Z]{3,}', text):
        score += 5  # Has section headers
    if re.search(r'\b\d{4}\b', text):
        score += 5  # Has dates
    if has_contact:
        score += 10
    if sections["projects"]:
        score += 10

    score = min(score, 100)
    return {"ats_score": score, "word_count": word_count, "sections": sections, "formatting_issues": issues, "suggestions": suggestions, "skills_found": skill_count}


def analyze_resume(filepath: str, target_role: str = "") -> dict:
    text = extract_text(filepath)
    if not text:
        return {"error": "Could not extract text from resume"}
    skills = detect_skills(text)
    ats_check = basic_ats_check(text, skills)
    return {
        "text": text,
        "skills_detected": skills,
        "ats_score": ats_check["ats_score"],
        "word_count": ats_check["word_count"],
        "sections": ats_check["sections"],
        "formatting_issues": ats_check["formatting_issues"],
        "suggestions": ats_check["suggestions"],
    }
