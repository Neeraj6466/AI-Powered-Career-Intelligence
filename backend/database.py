import sqlite3
import os

# ---------------- PATH ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "career.db")


# ---------------- CREATE DATABASE ----------------
def create_database():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    # ---------------- USERS TABLE (Step 1) ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,

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
       databases TEXT
    )
    """)
    
    # ---------------- EDUCATION TABLE (Step 2) ----------------
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

    connection.commit()

    connection.close()

    print("Database created successfully!")


# ---------------- RUN ----------------
if __name__ == "__main__":
    create_database()