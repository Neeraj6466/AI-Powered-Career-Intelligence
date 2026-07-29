import re

def calculate_ats_score(resume_text):

    score = 0
    feedback = []

    # ---------------- Contact Information ----------------
    if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", resume_text):
        score += 10
    else:
        feedback.append("Add Email Address")

    if re.search(r"\b\d{10}\b", resume_text):
        score += 10
    else:
        feedback.append("Add Phone Number")

    # ---------------- Education ----------------
    if any(word in resume_text.lower() for word in [
        "b.tech", "btech", "degree", "engineering",
        "university", "college"
    ]):
        score += 15
    else:
        feedback.append("Add Education Details")

    # ---------------- Skills ----------------
    if "skills" in resume_text.lower():
        score += 20
    else:
        feedback.append("Add Skills Section")

    # ---------------- Projects ----------------
    if "project" in resume_text.lower():
        score += 15
    else:
        feedback.append("Add Projects")

    # ---------------- Experience ----------------
    if "experience" in resume_text.lower():
        score += 15
    else:
        feedback.append("Add Experience")

    # ---------------- Certifications ----------------
    if "certification" in resume_text.lower() or "certificate" in resume_text.lower():
        score += 10
    else:
        feedback.append("Add Certifications")

    # ---------------- LinkedIn ----------------
    if "linkedin.com" in resume_text.lower():
        score += 5
    else:
        feedback.append("Add LinkedIn Profile")

    return score, feedback