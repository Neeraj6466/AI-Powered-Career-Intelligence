def check_resume_completeness(resume_text):

    resume = resume_text.lower()

    sections = {
        "Personal Details": any(word in resume for word in ["email", "phone"]),
        "Education": any(word in resume for word in ["education", "college", "university", "b.tech", "btech"]),
        "Skills": "skills" in resume,
        "Projects": "project" in resume,
        "Experience": "experience" in resume,
        "Certifications": any(word in resume for word in ["certification", "certificate"])
    }

    completed = sum(sections.values())
    score = int((completed / len(sections)) * 100)

    return score, sections