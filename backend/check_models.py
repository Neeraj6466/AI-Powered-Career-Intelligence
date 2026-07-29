import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file")
    exit()

# Configure Gemini
genai.configure(api_key=api_key)

try:
    print("✅ Connected to Gemini\n")
    print("Available Models:\n")

    for model in genai.list_models():
        if "generateContent" in model.supported_generation_methods:
            print(model.name)

except Exception as e:
    print("❌ Error:")
    print(e)