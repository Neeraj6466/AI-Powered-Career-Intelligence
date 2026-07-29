def match_resume_with_jd(resume_text, jd_text):

    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())

    matched = resume_words.intersection(jd_words)
    missing = jd_words - resume_words

    if len(jd_words) == 0:
        score = 0
    else:
        score = int((len(matched) / len(jd_words)) * 100)

    return score, list(matched), list(missing)