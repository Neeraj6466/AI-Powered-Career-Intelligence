def check_ats(resume_text):

    keywords = [
        "python",
        "sql",
        "flask",
        "html",
        "css",
        "javascript",
        "git",
        "github",
        "api"
    ]

    text = resume_text.lower()

    found = []
    missing = []

    for keyword in keywords:
        if keyword in text:
            found.append(keyword)
        else:
            missing.append(keyword)

    score = int((len(found) / len(keywords)) * 100)

    tips = []

    if score < 50:
        tips.append("Add more technical skills.")
        tips.append("Include project descriptions.")
        tips.append("Use ATS-friendly keywords.")

    elif score < 80:
        tips.append("Improve keyword matching.")
        tips.append("Add measurable achievements.")

    else:
        tips.append("Excellent ATS compatibility.")
        tips.append("Resume is well optimized.")

    return score, missing, tips