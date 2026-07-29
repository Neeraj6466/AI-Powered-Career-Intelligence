def find_missing_sections(resume_text):

    resume = resume_text.lower()

    checks = {
        "Experience": "experience",
        "Projects": "project",
        "Skills": "skills",
        "Education": "education",
        "Certifications": "certification",
        "Achievements": "achievement"
    }

    missing = []

    for section, keyword in checks.items():
        if keyword not in resume:
            missing.append(section)

    return missing