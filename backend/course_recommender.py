def recommend_courses(missing_skills):

    courses = {

        "TensorFlow": {
            "course": "TensorFlow for Beginners",
            "platform": "Coursera",
            "duration": "20 Hours",
            "level": "Beginner"
        },

        "PyTorch": {
            "course": "PyTorch Deep Learning",
            "platform": "Udemy",
            "duration": "18 Hours",
            "level": "Intermediate"
        },

        "Docker": {
            "course": "Docker Essentials",
            "platform": "Coursera",
            "duration": "12 Hours",
            "level": "Beginner"
        },

        "React": {
            "course": "React Complete Course",
            "platform": "Udemy",
            "duration": "24 Hours",
            "level": "Intermediate"
        },

        "Flask": {
            "course": "Flask Web Development",
            "platform": "Coursera",
            "duration": "16 Hours",
            "level": "Beginner"
        },

        "Django": {
            "course": "Django Masterclass",
            "platform": "Udemy",
            "duration": "22 Hours",
            "level": "Intermediate"
        },

        "Git": {
            "course": "Git & GitHub Bootcamp",
            "platform": "Coursera",
            "duration": "8 Hours",
            "level": "Beginner"
        },

        "SQL": {
            "course": "SQL for Data Analysis",
            "platform": "Coursera",
            "duration": "14 Hours",
            "level": "Beginner"
        },

        "Power BI": {
            "course": "Power BI Complete Guide",
            "platform": "Udemy",
            "duration": "18 Hours",
            "level": "Intermediate"
        },

        "Excel": {
            "course": "Advanced Excel",
            "platform": "Microsoft Learn",
            "duration": "10 Hours",
            "level": "Beginner"
        }
    }

    recommended = []

    for skill in missing_skills:
        if skill in courses:
            recommended.append({
                "skill": skill,
                "course": courses[skill]["course"],
                "platform": courses[skill]["platform"],
                "duration": courses[skill]["duration"],
                "level": courses[skill]["level"]
            })

    return recommended