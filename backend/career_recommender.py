def recommend_career(skills):

    skills = [skill.lower() for skill in skills]

    if "machine learning" in skills or "artificial intelligence" in skills:
        return "AI / Machine Learning Engineer"

    elif "flask" in skills or "django" in skills:
        return "Python Backend Developer"

    elif "react" in skills or "javascript" in skills:
        return "Frontend Developer"

    elif "sql" in skills and "python" in skills:
        return "Data Analyst"

    elif "python" in skills:
        return "Python Developer"

    else:
        return "Software Developer"