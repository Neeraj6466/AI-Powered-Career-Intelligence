import sqlite3
import os

# ---------------- PATH ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "career.db")


# ---------------- CREATE DATABASE ----------------
def create_database():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # ---------------- USERS TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',

        phone TEXT,
        dob TEXT,
        gender TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        country TEXT,

        profile_image TEXT,

        programming_languages TEXT,
        web_technologies TEXT,
        frameworks TEXT,
        databases TEXT,

        project_name TEXT,
        project_description TEXT,
        github_repo TEXT,
        tech_used TEXT,
        certifications TEXT,
        work_experience TEXT,
        career_interest TEXT
    )
    """)

    # ---------------- ADD MISSING COLUMNS TO EXISTING USERS TABLE ----------------
    # This is important because career.db already exists.

    profile_columns = {
        "role": "TEXT DEFAULT 'user'",
        "project_name": "TEXT",
        "project_description": "TEXT",
        "github_repo": "TEXT",
        "tech_used": "TEXT",
        "certifications": "TEXT",
        "work_experience": "TEXT",
        "career_interest": "TEXT"
    }

    # Get existing columns
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [column[1] for column in cursor.fetchall()]

    # Add missing columns
    for column_name, column_type in profile_columns.items():

        if column_name not in existing_columns:

            cursor.execute(
                f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
            )

    # ---------------- EDUCATION TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS education(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        college TEXT,
        degree TEXT,
        branch TEXT,
        university TEXT,
        cgpa TEXT,
        start_year TEXT,
        end_year TEXT
    )
    """)

    # ---------------- RESUME HISTORY TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resume_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        filename TEXT NOT NULL,
        score INTEGER,
        career TEXT,
        salary TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

        # ---------------- JOB POSTINGS TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_postings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT,
        location TEXT,
        description TEXT,
        skills TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # ---------------- COURSES TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    platform TEXT,
    category TEXT,
    url TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # ---------------- ANNOUNCEMENTS TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS announcements(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
        # ---------------- FEEDBACK TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        type TEXT NOT NULL,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # ---------------- ACTIVITY LOGS TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        action TEXT NOT NULL,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    connection.commit()
    connection.close()

    print("Database created successfully!")


# ---------------- CREATE ADMIN ----------------
def create_admin():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Check whether admin already exists
    cursor.execute(
        "SELECT id FROM users WHERE email=?",
        ("admin@gmail.com",)
    )

    existing_admin = cursor.fetchone()

    if existing_admin:

        # Make sure existing admin has admin role
        cursor.execute(
            "UPDATE users SET role='admin' WHERE email=?",
            ("admin@gmail.com",)
        )

        connection.commit()

        print("Admin already exists!")

    else:

        import bcrypt

        # Admin password
        password = "Admin@123"

        # Encrypt password
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # Insert admin
        cursor.execute("""
            INSERT INTO users(
                fullname,
                email,
                password,
                role
            )
            VALUES (?, ?, ?, ?)
        """, (
            "System Admin",
            "admin@gmail.com",
            hashed_password,
            "admin"
        ))

        connection.commit()

        print("Admin account created successfully!")

    connection.close()


# ---------------- RUN ----------------
if __name__ == "__main__":

    create_database()
    create_admin()