from flask import Flask, render_template, request, redirect, url_for, send_file, session
import sqlite3
import os
import bcrypt

from functools import wraps
from werkzeug.utils import secure_filename

from resume_parser import extract_text
from skill_extractor import extract_skills
from career_recommender import recommend_career
from missing_skills import get_missing_skills
from course_recommender import recommend_courses
from salary_predictor import predict_salary
from gemini_ai import analyze_resume
from pdf_generator import generate_report
from ats_score import calculate_ats_score 
from keyword_matcher import keyword_match 
from resume_completeness import check_resume_completeness 
from missing_sections import find_missing_sections 
from soft_skills import detect_soft_skills 
from experience_detector import detect_experience 
from profile_detector import detect_profiles 
from language_detector import detect_languages
from resume_job_match import calculate_match
from job_recommender import recommend_jobs
from interview_generator import generate_interview

app = Flask(__name__)

# ---------------- CONFIGURATION ----------------
app.secret_key = os.urandom(24)  # Secure secret key for tracking user sessions
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "career.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------- DECORATOR FOR PROTECTED ROUTES ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_email" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ---------------- HOME ----------------
@app.route("/")
def home():
    if "user_email" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match!"

        # Hash the plain-text password securely using bcrypt
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), 
            bcrypt.gensalt()
        ).decode("utf-8")

        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(fullname, email, password) VALUES (?, ?, ?)",
                (fullname, email, hashed_password)
            )
            connection.commit()
        except sqlite3.IntegrityError:
            connection.close()
            return "Email already exists!"

        connection.close()
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        # Query user data purely by email to evaluate the password programmatically
        cursor.execute(
            "SELECT fullname, password FROM users WHERE email=?",
            (email,)
        )
        user = cursor.fetchone()
        connection.close()

        # Check if the user exists and verify the hashed password matches
        if user and bcrypt.checkpw(password.encode("utf-8"), user[1].encode("utf-8")):
            session["user_email"] = email
            session["user_name"] = user[0]
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Email or Password!"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user_name=session.get("user_name"))

# ---------------- ATS ANALYSIS ----------------

@app.route("/ats-analysis", methods=["GET", "POST"])
@login_required
def ats_analysis():

    if request.method == "GET":
        return render_template("ats_analysis.html")

    resume = request.files["resume"]
    job_description = request.form["job_description"]

    filename = secure_filename(resume.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    resume.save(save_path)

    resume_text = extract_text(save_path)

    match_percentage, matching_skills, missing_skills = calculate_match(
        resume_text,
        job_description
    )

    # -------- Save data for Dashboard Analytics --------
    session["ats_score"] = match_percentage
    session["job_match"] = match_percentage
    session["matching_skills"] = matching_skills
    session["missing_skills"] = missing_skills

    return render_template(
        "ats_result.html",
        resume_text=resume_text,
        job_description=job_description,
        match_percentage=match_percentage,
        matching_skills=matching_skills,
        missing_skills=missing_skills
    )

# ---------------- SKILL GAP ANALYSIS ----------------

@app.route("/skill-gap", methods=["GET", "POST"])
@login_required
def skill_gap():

    if request.method == "GET":
        return render_template("skill_gap.html")

    resume = request.files["resume"]

    filename = secure_filename(resume.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    resume.save(save_path)

    resume_text = extract_text(save_path)

    skills = extract_skills(resume_text)

    career = request.form["career"]

    missing_skills = get_missing_skills(career, skills)

    courses = recommend_courses(missing_skills)

    # -------- Save data for Dashboard Analytics --------
    session["courses"] = courses
    session["missing_skills"] = missing_skills

    return render_template(
        "skill_gap_result.html",
        career=career,
        skills=skills,
        missing_skills=missing_skills,
        courses=courses
    )


# ---------------- DASHBOARD ANALYTICS ----------------

@app.route("/dashboard-analytics")
@login_required
def dashboard_analytics():

    ats_score = session.get("ats_score", 0)

    job_match = session.get("job_match", 0)

    matching_skills = session.get("matching_skills", [])

    missing_skills = session.get("missing_skills", [])

    career = session.get("career", "Not Available")

    courses = session.get("courses", [])

    salary = session.get("salary", "Not Available")

    resume_status = "Uploaded"

    profile = 90

    return render_template(
        "dashboard_analytics.html",
        ats_score=ats_score,
        resume_status=resume_status,
        job_match=job_match,
        profile=profile,
        matching_skills=matching_skills,
        missing_skills=missing_skills,
        career=career,
        courses=courses,
        salary=salary
    )
# ---------------- CAREER RECOMMENDATION ----------------

@app.route("/career-recommendation", methods=["GET", "POST"])
@login_required
def career_recommendation():

    if request.method == "GET":
        return render_template("career_recommendation.html")

    # Upload Resume
    resume = request.files["resume"]

    filename = secure_filename(resume.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    resume.save(save_path)

    # Extract Resume Text
    resume_text = extract_text(save_path)

    # Extract Skills
    skills = extract_skills(resume_text)

    # Recommend Career
    career = recommend_career(skills)

    # Predict Salary
    salary = predict_salary(career)

    # AI Analysis
    ai_analysis = analyze_resume(resume_text)

    # -------- Save data for Dashboard Analytics --------
    session["career"] = career
    session["salary"] = salary

    return render_template(
        "career_result.html",
        career=career,
        salary=salary,
        skills=skills,
        ai_analysis=ai_analysis
    )

#---------------- JOB RECOMMENDATION ----------------
@app.route("/job-recommendation", methods=["GET", "POST"])
@login_required
def job_recommendation():

    if request.method == "GET":
        return render_template("job_recommendation.html")

    resume = request.files["resume"]

    filename = secure_filename(resume.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    resume.save(save_path)

    resume_text = extract_text(save_path)

    skills = extract_skills(resume_text)

    jobs = recommend_jobs(skills)

    return render_template(
        "job_result.html",
        jobs=jobs,
        skills=skills
    )

#---------------- INTERVIEW PREPARATION ----------------
@app.route("/interview-preparation", methods=["GET", "POST"])
@login_required
def interview_preparation():

    if request.method == "GET":
        return render_template("interview_preparation.html")

    # Upload Resume
    resume = request.files["resume"]

    filename = secure_filename(resume.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    resume.save(save_path)

    # Extract Resume Text
    resume_text = extract_text(save_path)

    # Extract Skills
    skills = extract_skills(resume_text)

    # Recommend Career
    career = recommend_career(skills)

    # Generate Interview Questions
    interview = generate_interview(career)

    return render_template(
        "interview_result.html",
        career=career,
        technical=interview["technical"],
        hr=interview["hr"]
    )

#---------------- RESUME BUILDER ----------------
@app.route("/resume-builder", methods=["GET", "POST"])
@login_required
def resume_builder():

    if request.method == "GET":
        return render_template("resume_builder.html")

    data = {
        "name": request.form["name"],
        "email": request.form["email"],
        "phone": request.form["phone"],
        "address": request.form["address"],
        "education": request.form["education"],
        "experience": request.form["experience"],
        "skills": request.form["skills"],
        "projects": request.form["projects"]
    }

    return render_template(
        "resume_preview.html",
        data=data
    )



# ---------------- RESUME UPLOAD ----------------
@app.route("/upload", methods=["POST"])
@login_required
def upload():
    if "resume" not in request.files:
        return "No file selected!"

    file = request.files["resume"]

    if file.filename == "":
        return "No file selected!"

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    # Extract Resume Text
    try:
        resume_text = extract_text(save_path)
    except ValueError as e:
        return str(e)

    if not resume_text.strip():
        return "Unable to extract text from the resume."

    # Extract Skills
    skills = extract_skills(resume_text)

    # Career Recommendation
    career = recommend_career(skills)

    # Missing Skills
    missing_skills = get_missing_skills(career, skills)

    # Recommended Courses
    courses = recommend_courses(missing_skills)

    # Salary Prediction
    salary = predict_salary(career)

    # Gemini AI Analysis
    ai_analysis = analyze_resume(resume_text)
    
    # ATS Resume Score
    ats_score, ats_feedback = calculate_ats_score(resume_text)
    
    # Keyword Matching
    matched_keywords, missing_keywords = keyword_match(resume_text)
    
    # Resume Completeness Check
    completeness_score, resume_sections = check_resume_completeness(resume_text)
    
    # Missing Sections Check
    missing_sections = find_missing_sections(resume_text)
    
    # Soft Skills Detection
    soft_skills = detect_soft_skills(resume_text)
    
    # Experience Detection
    experience = detect_experience(resume_text)
    
    # Profile Detection
    linkedin, github = detect_profiles(resume_text)
    
    # Language Detection
    languages = detect_languages(resume_text)

    # Resume Score
    score = min(len(skills) * 5, 100)

    # ---------------- SAVE USER HISTORY ----------------
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    email = session["user_email"]

    cursor.execute("""
    INSERT INTO resume_history
    (email, filename, score, career, salary)
    VALUES (?, ?, ?, ?, ?)
    """, (
        email,
        filename,
        score,
        career,
        salary
    ))

    connection.commit()
    connection.close()

    # ---------------- GENERATE REPORT ----------------
    report_filename = f"resume_report_{email}.pdf"
    report_path = os.path.join(BASE_DIR, report_filename)
    
    generate_report(
        report_path,
        score,
        career,
        salary,
        skills,
        missing_skills,
        courses
    )

    return render_template(
    "result.html",
    score=score,
    career=career,
    salary=salary,
    skills=skills,
    missing_skills=missing_skills,
    courses=courses,
    ai_analysis=ai_analysis,
    ats_score=ats_score,
    ats_feedback=ats_feedback,
    resume_text=resume_text,
    matched_keywords=matched_keywords,
    missing_keywords=missing_keywords,
    completeness_score=completeness_score,
    resume_sections=resume_sections,
    missing_sections=missing_sections,
    report_filename=report_filename,
    soft_skills=soft_skills,
    experience=experience,
    linkedin=linkedin,
    github=github,
    languages=languages
)


# ---------------- USER HISTORY ----------------
@app.route("/history")
@login_required
def history():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT filename, score, career, salary, upload_date
    FROM resume_history
    WHERE email=?
    ORDER BY upload_date DESC
    """, (session["user_email"],))

    user_history = cursor.fetchall()

    connection.close()

    return render_template(
        "history.html",
        history=user_history
    )


# ---------------- RESUME MANAGEMENT ----------------
@app.route("/resume-management")
@login_required
def resume_management():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT filename, upload_date
    FROM resume_history
    WHERE email=?
    ORDER BY upload_date DESC
    """, (session["user_email"],))

    resumes = cursor.fetchall()

    connection.close()

    return render_template(
        "resume_management.html",
        resumes=resumes
    )

# ---------------- VIEW RESUME ----------------
@app.route("/view-resume/<filename>")
@login_required
def view_resume(filename):

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if os.path.exists(file_path):
        return send_file(file_path)

    return "Resume not found!"

# ---------------- DOWNLOAD RESUME ----------------
@app.route("/download-resume/<filename>")
@login_required
def download_resume(filename):

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )

    return "Resume not found!"

# ---------------- REPLACE RESUME ----------------
@app.route("/replace-resume/<filename>", methods=["GET", "POST"])
@login_required
def replace_resume(filename):

    old_file = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if request.method == "POST":

        if "resume" not in request.files:
            return "No file selected!"

        new_file = request.files["resume"]

        if new_file.filename == "":
            return "No file selected!"

        new_filename = secure_filename(new_file.filename)
        new_path = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)

        # Delete old file if it exists
        if os.path.exists(old_file):
            os.remove(old_file)

        # Save new file
        new_file.save(new_path)

        # Update database
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE resume_history
            SET filename = ?
            WHERE email = ? AND filename = ?
        """, (
            new_filename,
            session["user_email"],
            filename
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("resume_management"))

    return render_template("replace_resume.html", filename=filename)


# ---------------- DELETE RESUME ----------------
@app.route("/delete-resume/<filename>")
@login_required
def delete_resume(filename):

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    # Delete the resume file
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete the record from the database
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM resume_history
        WHERE email=? AND filename=?
    """, (
        session["user_email"],
        filename
    ))

    connection.commit()
    connection.close()

    return redirect(url_for("resume_management"))

# ---------------- USER PROFILE ----------------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    email = session["user_email"]

    if request.method == "POST":

        # ---------------- PERSONAL INFO ----------------
        fullname = request.form.get("fullname")
        phone = request.form.get("phone")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")
        country = request.form.get("country")
        programming_languages = request.form.get("programming_languages")
        web_technologies = request.form.get("web_technologies")
        frameworks = request.form.get("frameworks")
        databases = request.form.get("databases")
        project_name = request.form.get("project_name")
        project_description = request.form.get("project_description")
        github_repo = request.form.get("github_repo")
        tech_used = request.form.get("tech_used")
        certifications = request.form.get("certifications")
        work_experience = request.form.get("work_experience")
        career_interest = request.form.get("career_interest")

        cursor.execute("""
        UPDATE users
        SET
fullname=?,
phone=?,
dob=?,
gender=?,
address=?,
city=?,
state=?,
country=?,
programming_languages=?,
web_technologies=?,
frameworks=?,
databases=?,
project_name=?,
project_description=?,
github_repo=?,
tech_used=?,
certifications=?,
work_experience=?,
career_interest=?
WHERE email=?
        """, (
    fullname,
    phone,
    dob,
    gender,
    address,
    city,
    state,
    country,
    programming_languages,
    web_technologies,
    frameworks,
    databases,
    project_name,
    project_description,
    github_repo,
    tech_used,
    certifications,
    work_experience,
    career_interest,
    email
))

        

        # ---------------- SAVE EDUCATION ----------------

        cursor.execute("DELETE FROM education WHERE email=?", (email,))

        colleges = request.form.getlist("college[]")
        degrees = request.form.getlist("degree[]")
        branches = request.form.getlist("branch[]")
        cgpas = request.form.getlist("cgpa[]")
        starts = request.form.getlist("start_year[]")
        ends = request.form.getlist("end_year[]")

        for i in range(len(colleges)):
            if colleges[i].strip() != "":
                cursor.execute("""
                INSERT INTO education
                (
                    email,
                    college,
                    degree,
                    branch,
                    cgpa,
                    start_year,
                    end_year
                )
                VALUES(?,?,?,?,?,?,?)
                """, (
                    email,
                    colleges[i],
                    degrees[i],
                    branches[i],
                    cgpas[i],
                    starts[i],
                    ends[i]
                ))
        connection.commit()
        connection.close()
        return redirect(url_for("profile"))

    # ---------------- USER DETAILS ----------------

    cursor.execute("""
SELECT
fullname,
email,
phone,
dob,
gender,
address,
city,
state,
country,
profile_image,
programming_languages,
web_technologies,
frameworks,
databases,
project_name,
project_description,
github_repo,
tech_used,
certifications,
work_experience,
career_interest
FROM users
WHERE email=?
""", (email,))

    user = cursor.fetchone()

    # ---------------- EDUCATION ----------------

    cursor.execute("""
    SELECT
    college,
    degree,
    branch,
    cgpa,
    start_year,
    end_year
    FROM education
    WHERE email=?
    """, (email,))

    education = cursor.fetchall()

    # ---------------- DASHBOARD DATA ----------------

    cursor.execute("""
    SELECT COUNT(*)
    FROM resume_history
    WHERE email=?
    """, (email,))
    total_uploads = cursor.fetchone()[0]

    cursor.execute("""
    SELECT score, career
    FROM resume_history
    WHERE email=?
    ORDER BY upload_date DESC
    LIMIT 1
    """, (email,))

    latest = cursor.fetchone()

    connection.close()

    if latest:
        latest_score = latest[0]
        latest_career = latest[1]
    else:
        latest_score = 0
        latest_career = "Not Available"

    return render_template(
        "profile.html",
        user=user,
        education=education,
        total_uploads=total_uploads,
        latest_score=latest_score,
        latest_career=latest_career
    )


# ---------------- DOWNLOAD TARGET REPORT ----------------
@app.route("/download-report")
@login_required
def download_report():
    email = session["user_email"]
    report_filename = f"resume_report_{email}.pdf"
    report_path = os.path.join(BASE_DIR, report_filename)

    if os.path.exists(report_path):
        return send_file(
            report_path,
            as_attachment=True,
            download_name="AI_Career_Report.pdf"
        )

    return "Report not found! Please upload your resume to generate one."


# ---------------- LOGOUT ----------------
@app.route("/logout")
@login_required
def logout():
    session.clear()  # Wipes the active user session keys cleanly
    return redirect(url_for("home"))


    # ---------------- INTERVIEW TOPIC ----------------

@app.route("/interview-topic/<topic>")
@login_required
def interview_topic(topic):

    interview_data = {
        "python": [

{"question":"What is Python?","answer":"Python is a high-level, interpreted programming language."},

{"question":"What are the features of Python?","answer":"Easy syntax, interpreted, object-oriented, portable and open-source."},

{"question":"What is List?","answer":"A List is a mutable collection in Python."},

{"question":"What is Tuple?","answer":"Tuple is an immutable collection."},

{"question":"Difference between List and Tuple?","answer":"List can be modified, Tuple cannot."},

{"question":"What is Dictionary?","answer":"Dictionary stores data as key-value pairs."},

{"question":"What is Set?","answer":"Set stores unique values only."},

{"question":"What is Function?","answer":"A reusable block of code."},

{"question":"What is Lambda Function?","answer":"An anonymous function created using lambda keyword."},

{"question":"What is Recursion?","answer":"A function calling itself."}

],
        "machine-learning": [

{"question":"What is Machine Learning?","answer":"Machine Learning is a branch of AI that enables computers to learn from data without being explicitly programmed."},

{"question":"What are the types of Machine Learning?","answer":"Supervised Learning, Unsupervised Learning and Reinforcement Learning."},

{"question":"What is Supervised Learning?","answer":"It is a learning method that uses labeled training data."},

{"question":"What is Unsupervised Learning?","answer":"It is a learning method that finds hidden patterns from unlabeled data."},

{"question":"What is Reinforcement Learning?","answer":"An agent learns by interacting with an environment using rewards and penalties."},

{"question":"What is Overfitting?","answer":"A model performs well on training data but poorly on unseen data."},

{"question":"What is Underfitting?","answer":"A model is too simple and performs poorly on both training and testing data."},

{"question":"What is a Dataset?","answer":"A collection of data used for training and testing machine learning models."},

{"question":"What is Feature Engineering?","answer":"The process of selecting and transforming variables to improve model performance."},

{"question":"What is Cross Validation?","answer":"A technique used to evaluate machine learning models using multiple data splits."}

],
        "deep-learning": [

{"question":"What is Deep Learning?","answer":"Deep Learning is a subset of Machine Learning that uses neural networks with multiple hidden layers."},

{"question":"What is an Artificial Neural Network (ANN)?","answer":"ANN is a computing model inspired by the human brain, consisting of interconnected neurons."},

{"question":"What is a Perceptron?","answer":"A Perceptron is the simplest type of neural network used for binary classification."},

{"question":"What is a Hidden Layer?","answer":"A hidden layer is the layer between the input and output layers where feature learning happens."},

{"question":"What is an Activation Function?","answer":"It decides whether a neuron should be activated. Examples include ReLU, Sigmoid, and Tanh."},

{"question":"What is ReLU?","answer":"ReLU (Rectified Linear Unit) returns x if x > 0, otherwise 0."},

{"question":"What is Backpropagation?","answer":"Backpropagation updates neural network weights by minimizing prediction error."},

{"question":"What is CNN?","answer":"Convolutional Neural Networks are mainly used for image processing and computer vision."},

{"question":"What is RNN?","answer":"Recurrent Neural Networks are designed for sequential data such as text and speech."},

{"question":"What is LSTM?","answer":"Long Short-Term Memory is a special type of RNN that remembers long-term dependencies."}

],
        "sql": [

{"question":"What is SQL?","answer":"SQL (Structured Query Language) is used to store, retrieve, update and manage data in relational databases."},

{"question":"What is the difference between SQL and MySQL?","answer":"SQL is a language, while MySQL is a relational database management system."},

{"question":"What is a Primary Key?","answer":"A Primary Key uniquely identifies each record in a table."},

{"question":"What is a Foreign Key?","answer":"A Foreign Key creates a relationship between two tables."},

{"question":"What is the difference between DELETE, DROP and TRUNCATE?","answer":"DELETE removes selected rows, TRUNCATE removes all rows, DROP removes the entire table."},

{"question":"What is a JOIN?","answer":"A JOIN combines rows from two or more tables based on a related column."},

{"question":"Types of JOINs?","answer":"INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN and CROSS JOIN."},

{"question":"What is a View?","answer":"A View is a virtual table created using an SQL query."},

{"question":"What is Normalization?","answer":"Normalization reduces data redundancy and improves database efficiency."},

{"question":"What is an Index?","answer":"An Index improves the speed of data retrieval operations."}

],
        "tensorflow": [

{"question":"What is TensorFlow?","answer":"TensorFlow is an open-source machine learning framework developed by Google for building and training deep learning models."},

{"question":"Who developed TensorFlow?","answer":"TensorFlow was developed by the Google Brain team."},

{"question":"What are the main features of TensorFlow?","answer":"Open-source, scalable, supports CPU/GPU/TPU, automatic differentiation, and production deployment."},

{"question":"What is a Tensor?","answer":"A Tensor is a multi-dimensional array and is the basic data structure used in TensorFlow."},

{"question":"What is TensorFlow Keras?","answer":"TensorFlow Keras is the high-level API used to build and train deep learning models easily."},

{"question":"What is Sequential Model?","answer":"A Sequential Model is a linear stack of layers where each layer has one input and one output."},

{"question":"What are Epochs in TensorFlow?","answer":"An epoch is one complete pass of the entire training dataset through the neural network."},

{"question":"What is Batch Size?","answer":"Batch size is the number of training samples processed before updating the model weights."},

{"question":"What is Gradient Descent?","answer":"Gradient Descent is an optimization algorithm used to minimize the loss function during training."},

{"question":"What is TensorBoard?","answer":"TensorBoard is TensorFlow's visualization tool used to monitor training, graphs, and performance metrics."}

],
        "dbms": [

{"question":"What is DBMS?","answer":"DBMS (Database Management System) is software used to create, store, retrieve, update and manage databases."},

{"question":"What are the advantages of DBMS?","answer":"Reduces redundancy, improves security, ensures data consistency, supports backup and recovery."},

{"question":"What is the difference between DBMS and RDBMS?","answer":"DBMS stores data in files, while RDBMS stores data in related tables using relationships."},

{"question":"What is Normalization?","answer":"Normalization organizes data to reduce redundancy and improve consistency."},

{"question":"What are the normal forms?","answer":"1NF, 2NF, 3NF, BCNF, 4NF and 5NF."},

{"question":"What is a Primary Key?","answer":"A Primary Key uniquely identifies every record in a table."},

{"question":"What is a Foreign Key?","answer":"A Foreign Key creates relationships between two tables."},

{"question":"What is SQL?","answer":"SQL is the language used to communicate with relational databases."},

{"question":"What is ACID Property?","answer":"ACID stands for Atomicity, Consistency, Isolation and Durability."},

{"question":"What is Transaction?","answer":"A transaction is a sequence of database operations executed as a single unit."}

],
        "operating-system": [

{"question":"What is an Operating System?","answer":"An Operating System (OS) is system software that manages computer hardware, software resources, and provides services for applications."},

{"question":"What are the main functions of an Operating System?","answer":"Process management, memory management, file management, device management, security, and user interface."},

{"question":"What are the types of Operating Systems?","answer":"Batch OS, Time-Sharing OS, Distributed OS, Real-Time OS, Network OS, and Multiprocessing OS."},

{"question":"What is a Process?","answer":"A Process is a program that is currently being executed."},

{"question":"What is a Thread?","answer":"A Thread is the smallest unit of CPU execution within a process."},

{"question":"What is the difference between Process and Thread?","answer":"A Process has its own memory space, whereas threads share the same memory within a process."},

{"question":"What is CPU Scheduling?","answer":"CPU Scheduling is the process of selecting which process gets CPU time next."},

{"question":"What are the types of CPU Scheduling Algorithms?","answer":"FCFS, SJF, Priority Scheduling, Round Robin, and Multilevel Queue Scheduling."},

{"question":"What is Deadlock?","answer":"Deadlock is a situation where two or more processes wait indefinitely for resources held by each other."},

{"question":"What is Virtual Memory?","answer":"Virtual Memory is a memory management technique that uses disk space as an extension of RAM."}

],
        "computer-networks": [

{"question":"What is a Computer Network?","answer":"A Computer Network is a group of interconnected computers that communicate and share resources."},

{"question":"What are the types of Computer Networks?","answer":"LAN, MAN, WAN, PAN and CAN."},

{"question":"What is the OSI Model?","answer":"OSI (Open Systems Interconnection) is a 7-layer networking model used for communication."},

{"question":"Name the 7 layers of the OSI Model.","answer":"Physical, Data Link, Network, Transport, Session, Presentation and Application."},

{"question":"What is the TCP/IP Model?","answer":"TCP/IP is a networking model consisting of Application, Transport, Internet and Network Access layers."},

{"question":"What is an IP Address?","answer":"An IP Address is a unique address assigned to a device on a network."},

{"question":"What is the difference between TCP and UDP?","answer":"TCP is connection-oriented and reliable, whereas UDP is connectionless and faster."},

{"question":"What is DNS?","answer":"DNS (Domain Name System) translates domain names into IP addresses."},

{"question":"What is HTTP and HTTPS?","answer":"HTTP transfers web pages, while HTTPS is the secure version using SSL/TLS encryption."},

{"question":"What is a Router?","answer":"A Router connects different networks and forwards data packets between them."}

],
        "number-system": [

{
"question":"📖 Concept",
"answer":"A Number System is a way of representing numbers using digits. The most common number system is the Decimal Number System (Base 10)."
},

{
"question":"📐 Important Types",
"answer":"Natural Numbers (1,2,3...), Whole Numbers (0,1,2...), Integers (...,-2,-1,0,1,2...), Rational Numbers, Irrational Numbers, Real Numbers."
},

{
"question":"📖 Formula / Trick",
"answer":"Even Number = Divisible by 2\nOdd Number = Not divisible by 2\nPrime Number = Has exactly two factors (1 and itself)."
},

{
"question":"✅ Easy Example",
"answer":"Is 37 a Prime Number?\n\nFactors of 37 are only 1 and 37.\n\nAnswer: Yes, it is a Prime Number."
},

{
"question":"🎯 Interview Question 1",
"answer":"Find the HCF of 12 and 18.\n\nFactors of 12 = 1,2,3,4,6,12\nFactors of 18 = 1,2,3,6,9,18\n\nAnswer = 6"
},

{
"question":"🎯 Interview Question 2",
"answer":"Find the LCM of 12 and 18.\n\nLCM = 36"
},

{
"question":"🎯 Interview Question 3",
"answer":"Which of the following is an even number?\nA) 25\nB) 48\nC) 67\nD) 91\n\nAnswer = 48"
},

{
"question":"📝 Practice Question 1",
"answer":"Find the HCF of 24 and 36.\n\nAnswer = 12"
},

{
"question":"📝 Practice Question 2",
"answer":"Find the LCM of 15 and 20.\n\nAnswer = 60"
},

{
"question":"💡 Shortcut",
"answer":"To find HCF, list common factors or use prime factorization.\nTo find LCM, use:\nLCM × HCF = Product of the two numbers."
}

],
        "percentage": [

{
"question":"📖 Concept",
"answer":"Percentage means 'per hundred'. It is used to express a number as a part of 100."
},

{
"question":"📐 Formula",
"answer":"Percentage = (Value / Total Value) × 100"
},

{
"question":"✅ Easy Example",
"answer":"Find 20% of 500.\n\n20/100 × 500 = 100\n\nAnswer = 100"
},

{
"question":"🎯 Interview Question 1",
"answer":"A student scored 360 marks out of 450.\n\nPercentage = (360/450) × 100 = 80%"
},

{
"question":"🎯 Interview Question 2",
"answer":"Increase ₹500 by 10%.\n\n10% of 500 = 50\n\nNew Price = ₹550"
},

{
"question":"📝 Practice Question",
"answer":"A shopkeeper gives a 15% discount on ₹2000.\n\nClick 'Show Answer' to see the solution.\n\nAnswer = ₹300"
}

],
        "blood-relations":[

{
"question":"Who is your father's brother?",
"answer":"He is your Uncle."
},

{
"question":"Who is your mother's sister?",
"answer":"She is your Aunt."
},

{
"question":"Who is your brother's son?",
"answer":"He is your Nephew."
},

{
"question":"Who is your sister's daughter?",
"answer":"She is your Niece."
},

{
"question":"Easy Example",
"answer":"Ram is the son of Shyam. Shyam is the brother of Ravi. Ravi is Ram's Uncle."
}

], 
        "hr-interview":[

{
"question":"Tell me about yourself.",
"answer":"Introduce yourself briefly, including your education, skills, projects, and career goals."
},

{
"question":"Why should we hire you?",
"answer":"Explain your strengths, technical skills, willingness to learn, and how you can contribute to the company."
},

{
"question":"What are your strengths?",
"answer":"Example: Quick learner, problem-solving, teamwork, adaptability, and communication."
},

{
"question":"What are your weaknesses?",
"answer":"Mention a genuine weakness and explain how you are improving it."
},

{
"question":"Why do you want to join our company?",
"answer":"Talk about the company's reputation, learning opportunities, and career growth."
},

{
"question":"Where do you see yourself in 5 years?",
"answer":"I want to become a skilled software engineer and contribute to meaningful projects."
},

{
"question":"Describe your final-year project.",
"answer":"Explain the project objective, technologies used, your role, and the outcome."
},

{
"question":"Are you willing to relocate?",
"answer":"Yes, I am open to relocation based on the company's requirements."
},

{
"question":"Why did you choose Computer Science?",
"answer":"Because I enjoy solving problems, programming, and building software solutions."
},

{
"question":"Do you have any questions for us?",
"answer":"Yes. Ask about training, team structure, or career growth opportunities."
}

], 
        "general-knowledge":[

{
"question":"🇮🇳 What is the capital of India?",
"answer":"New Delhi."
},

{
"question":"🌍 Which is the largest continent?",
"answer":"Asia."
},

{
"question":"🏛️ Who is known as the Father of the Indian Constitution?",
"answer":"Dr. B. R. Ambedkar."
},

{
"question":"🛰️ Which organization launched the Chandrayaan missions?",
"answer":"ISRO (Indian Space Research Organisation)."
},

{
"question":"💻 What does CPU stand for?",
"answer":"Central Processing Unit."
},

{
"question":"🌐 What is the full form of WWW?",
"answer":"World Wide Web."
},

{
"question":"🏆 Which country won the 2023 Cricket World Cup?",
"answer":"Australia."
},

{
"question":"🧪 What is the chemical symbol for Gold?",
"answer":"Au."
},

{
"question":"📅 How many states are there in India?",
"answer":"28 States."
},

{
"question":"🚀 Which company developed ChatGPT?",
"answer":"OpenAI."
}

], 
        "company-wise":[

{
"question":"🏢 TCS Recruitment Process",
"answer":"Online Aptitude Test → Technical Interview → HR Interview."
},

{
"question":"🏢 Infosys Recruitment Process",
"answer":"Online Assessment → Technical Interview → HR Interview."
},

{
"question":"🏢 Wipro Recruitment Process",
"answer":"Aptitude Test → Coding Test → Technical Interview → HR Interview."
},

{
"question":"🏢 Accenture Recruitment Process",
"answer":"Cognitive Assessment → Coding → Communication Assessment → Technical & HR Interview."
},

{
"question":"🏢 Google Recruitment Process",
"answer":"Resume Screening → Online Assessment → Coding Interviews → System Design → HR."
},

{
"question":"🏢 Amazon Recruitment Process",
"answer":"Online Assessment → Technical Interviews → Leadership Principles Round → HR."
},

{
"question":"💻 Technical Preparation",
"answer":"Prepare DSA, OOPs, DBMS, SQL, OS, Computer Networks and Coding Problems."
},

{
"question":"📚 Aptitude Preparation",
"answer":"Practice Quantitative Aptitude, Logical Reasoning and Verbal Ability."
},

{
"question":"👨‍💼 HR Preparation",
"answer":"Prepare Self Introduction, Projects, Strengths, Weaknesses and Career Goals."
},

{
"question":"🌐 Official Career Websites",
"answer":"Visit the official career pages of TCS, Infosys, Wipro, Accenture, Google and Amazon for current job openings."
}

]
    }

    resources = {

    "python":[
        {"name":"GeeksforGeeks","desc":"Python Interview Questions","url":"https://www.geeksforgeeks.org/python-programming-language/"},
        {"name":"W3Schools","desc":"Learn Python","url":"https://www.w3schools.com/python/"},
        {"name":"Real Python","desc":"Python Tutorials","url":"https://realpython.com/"},
        {"name":"Python Docs","desc":"Official Documentation","url":"https://docs.python.org/3/"}
    ],

    "machine-learning":[
        {"name":"Kaggle","desc":"ML Datasets & Practice","url":"https://www.kaggle.com/"},
        {"name":"Scikit-Learn","desc":"ML Documentation","url":"https://scikit-learn.org/"},
        {"name":"Google ML Crash Course","desc":"Learn ML","url":"https://developers.google.com/machine-learning/crash-course"},
        {"name":"Papers With Code","desc":"Research Papers","url":"https://paperswithcode.com/"}
    ],

    "general-knowledge":[
        {"name":"GKToday","desc":"Current Affairs & GK","url":"https://www.gktoday.in/"},
        {"name":"Jagran Josh","desc":"GK & Exams","url":"https://www.jagranjosh.com/"},
        {"name":"AffairsCloud","desc":"Daily Current Affairs","url":"https://affairscloud.com/"},
        {"name":"Testbook GK","desc":"GK Practice","url":"https://testbook.com/"}
    ],

    "company-wise":[
        {"name":"LinkedIn Jobs","desc":"Latest Jobs","url":"https://www.linkedin.com/jobs/"},
        {"name":"Glassdoor","desc":"Interview Experience","url":"https://www.glassdoor.com/"},
        {"name":"AmbitionBox","desc":"Company Reviews","url":"https://www.ambitionbox.com/"},
        {"name":"Naukri","desc":"Company Openings","url":"https://www.naukri.com/"}
    ],

    "aptitude":[
        {"name":"IndiaBix","desc":"Aptitude Practice","url":"https://www.indiabix.com/"},
        {"name":"PrepInsta","desc":"Placement Preparation","url":"https://prepinsta.com/"},
        {"name":"Testbook","desc":"Aptitude Questions","url":"https://testbook.com/"},
        {"name":"FreshersNow","desc":"Placement Preparation","url":"https://www.freshersnow.com/"}
    ],

    "reasoning":[
        {"name":"IndiaBix","desc":"Reasoning Practice","url":"https://www.indiabix.com/logical-reasoning/"},
        {"name":"PrepInsta","desc":"Reasoning Questions","url":"https://prepinsta.com/"},
        {"name":"Testbook","desc":"Logical Reasoning","url":"https://testbook.com/"},
        {"name":"FreshersNow","desc":"Reasoning","url":"https://www.freshersnow.com/"}
    ],

    "hr-interview":[
        {"name":"Glassdoor","desc":"HR Questions","url":"https://www.glassdoor.com/Interview/"},
        {"name":"Indeed","desc":"Interview Guide","url":"https://www.indeed.com/career-advice"},
        {"name":"AmbitionBox","desc":"Interview Experience","url":"https://www.ambitionbox.com/interviews"},
        {"name":"LinkedIn","desc":"Career Advice","url":"https://www.linkedin.com/"}
    ]
}

    questions = interview_data.get(topic, [])


    return render_template(
    "interview_topic.html",
    title=topic.replace("-", " ").title(),
    questions=questions,
    resources=(
        resources["aptitude"] if topic in ["number-system", "percentage"] else
        resources["reasoning"] if topic in ["blood-relations"] else
        resources["python"] if topic in ["python", "sql", "dbms", "operating-system", "computer-networks"] else
        resources["machine-learning"] if topic in ["machine-learning", "deep-learning", "tensorflow"] else
        resources["general-knowledge"] if topic == "general-knowledge" else
        resources["company-wise"] if topic == "company-wise" else
        resources["hr-interview"] if topic == "hr-interview" else
        []
    )
)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)