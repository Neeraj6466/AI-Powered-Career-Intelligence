def detect_languages(resume_text):

    resume = resume_text.lower()

    languages = [
        "english",
        "telugu",
        "hindi",
        "tamil",
        "kannada",
        "malayalam",
        "marathi",
        "urdu",
        "french",
        "german",
        "spanish"
    ]

    found = []

    for language in languages:
        if language in resume:
            found.append(language.title())

    if not found:
        found.append("Not Mentioned")

    return found