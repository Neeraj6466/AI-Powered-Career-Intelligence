def keyword_match(resume_text):

    keywords = [
        "Python",
        "Java",
        "C++",
        "JavaScript",
        "HTML",
        "CSS",
        "Flask",
        "Django",
        "SQL",
        "MySQL",
        "SQLite",
        "Machine Learning",
        "Deep Learning",
        "Artificial Intelligence",
        "TensorFlow",
        "PyTorch",
        "Git",
        "GitHub",
        "Docker",
        "AWS",
        "React",
        "Node.js"
    ]

    matched = []
    missing = []

    resume = resume_text.lower()

    for keyword in keywords:
        if keyword.lower() in resume:
            matched.append(keyword)
        else:
            missing.append(keyword)

    return matched, missing