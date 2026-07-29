def get_missing_skills(career, skills):

    career_skills = {
        "AI / Machine Learning Engineer": [
            "Python",
            "Machine Learning",
            "Deep Learning",
            "TensorFlow",
            "PyTorch",
            "SQL",
            "Git",
            "Docker"
        ],

        "Python Backend Developer": [
            "Python",
            "Flask",
            "Django",
            "SQL",
            "Git",
            "Docker"
        ],

        "Frontend Developer": [
            "HTML",
            "CSS",
            "JavaScript",
            "React",
            "Git"
        ],

        "Data Analyst": [
            "Python",
            "SQL",
            "Pandas",
            "NumPy",
            "Power BI",
            "Excel"
        ],

        "Python Developer": [
            "Python",
            "Flask",
            "SQL",
            "Git"
        ]
    }

    required = career_skills.get(career, [])

    missing = []

    user_skills = [skill.lower() for skill in skills]

    for skill in required:
        if skill.lower() not in user_skills:
            missing.append(skill)

    return missing