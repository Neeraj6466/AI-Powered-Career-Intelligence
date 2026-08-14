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
    
    # ---------------- AI CHATBOT ----------------

def career_chatbot(user_message):

    prompt = f"""
You are an AI Career Assistant inside an AI Career Platform.

Your job is to help users with:
- Resume Analysis
- ATS Analysis
- Skill Gap Analysis
- Career Recommendations
- Job Recommendations
- Interview Preparation
- Aptitude
- Reasoning
- Technical subjects
- HR Interviews
- General Knowledge
- Company-wise interview preparation
- Programming and AI/ML concepts
- Career guidance

IMPORTANT LANGUAGE RULE:
Understand the language used by the user.

If the user asks in Telugu, answer in simple Telugu.
If the user asks in Hindi, answer in simple Hindi.
If the user asks in English, answer in simple English.
If the user mixes languages, understand the meaning and answer naturally in the same style.

IMPORTANT:
- Explain difficult concepts in simple words.
- Give practical examples whenever useful.
- Keep answers relevant to the user's question.
- Do not unnecessarily give very long answers.
- If the question is related to this AI Career Platform, explain the relevant feature clearly.
- If the user asks about programming or technical concepts, give simple examples.
- Be friendly and helpful.

User Question:
{user_message}

Answer:
"""

    try:

        if model is None:
            return "Gemini API key is not configured."

        response = model.generate_content(prompt)

        if response and hasattr(response, "text"):
            return response.text

        return "Sorry, I couldn't generate a response."

    except Exception as e:
        return f"Chatbot Error:\n{str(e)}"