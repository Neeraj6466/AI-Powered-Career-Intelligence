import re

def detect_experience(resume_text):

    resume = resume_text.lower()

    match = re.search(r'(\d+)\+?\s*(year|years)', resume)

    if match:
        return f"{match.group(1)} Years"

    if "fresher" in resume:
        return "Fresher"

    return "Not Mentioned"