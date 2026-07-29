def extract_skills(resume_text):

    skills_list = [
        "Python",
        "Java",
        "C",
        "C++",
        "HTML",
        "CSS",
        "JavaScript",
        "SQL",
        "Flask",
        "Django",
        "React",
        "Node.js",
        "Machine Learning",
        "Deep Learning",
        "Artificial Intelligence",
        "Data Science",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow",
        "Git",
        "GitHub",
        "MongoDB"
    ]

    found_skills = []

    resume_text = resume_text.lower()

    for skill in skills_list:
        if skill.lower() in resume_text:
            found_skills.append(skill)

    return found_skills