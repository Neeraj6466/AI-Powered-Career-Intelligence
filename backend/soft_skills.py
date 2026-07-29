def detect_soft_skills(resume_text):

    resume = resume_text.lower()

    skills = [
        "communication",
        "teamwork",
        "leadership",
        "problem solving",
        "time management",
        "adaptability",
        "critical thinking",
        "creativity"
    ]

    found = []

    for skill in skills:
        if skill in resume:
            found.append(skill.title())

    if not found:
        found.append("No soft skills detected")

    return found