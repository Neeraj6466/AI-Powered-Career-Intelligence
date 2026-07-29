def predict_salary(career):

    salaries = {

        "AI / Machine Learning Engineer": "₹6 LPA - ₹12 LPA",

        "Python Backend Developer": "₹5 LPA - ₹10 LPA",

        "Frontend Developer": "₹4 LPA - ₹9 LPA",

        "Data Analyst": "₹4 LPA - ₹8 LPA",

        "Python Developer": "₹4 LPA - ₹8 LPA",

        "Software Developer": "₹4 LPA - ₹9 LPA"

    }

    return salaries.get(career, "Salary Not Available")