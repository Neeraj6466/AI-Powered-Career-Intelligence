import re

SKILLS = [
    "python", "java", "c", "c++", "html", "css", "javascript",
    "flask", "django", "react", "node.js", "sql", "mysql",
    "mongodb", "git", "github", "tensorflow", "keras",
    "machine learning", "deep learning", "artificial intelligence",
    "numpy", "pandas", "opencv", "aws", "docker"
]

def calculate_match(resume_text, job_description):

    resume = resume_text.lower()
    job = job_description.lower()

    matching_skills = []
    missing_skills = []

    for skill in SKILLS:
        if skill in job:
            if skill in resume:
                matching_skills.append(skill.title())
            else:
                missing_skills.append(skill.title())

    total = len(matching_skills) + len(missing_skills)

    if total == 0:
        percentage = 0
    else:
        percentage = round((len(matching_skills) / total) * 100)

    return percentage, matching_skills, missing_skills