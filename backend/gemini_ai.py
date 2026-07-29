import os
from dotenv import load_dotenv
import google.generativeai as genai

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

API_KEY = os.getenv("GEMINI_API_KEY")
model = None

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("models/gemini-flash-latest")


def analyze_resume(resume_text):

    prompt = f"""
You are an expert AI Career Advisor.

Analyze the following resume.

Provide your answer in this format:

1. Resume Summary

2. Recommended Career

3. Strengths

4. Weaknesses

5. Missing Skills

6. Learning Roadmap

7. Interview Preparation Tips

8. Final Career Advice

Resume:

{resume_text}
"""

    try:
        response = model.generate_content(prompt)

        if response and hasattr(response, "text"):
            return response.text

        return "No response generated from Gemini."

    except Exception as e:
        return f"Gemini AI Error:\n{str(e)}"