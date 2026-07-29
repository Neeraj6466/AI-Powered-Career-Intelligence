from interview_questions import questions

def generate_interview(career):

    return questions.get(
        career,
        {
            "technical": [],
            "hr": []
        }
    )