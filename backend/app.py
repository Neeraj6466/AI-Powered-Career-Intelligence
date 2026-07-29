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


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)