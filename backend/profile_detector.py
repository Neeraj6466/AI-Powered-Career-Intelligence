import re

def detect_profiles(resume_text):

    linkedin = "Not Found"
    github = "Not Found"

    linkedin_match = re.search(r'https?://(?:www\.)?linkedin\.com/[^\s]+', resume_text)
    github_match = re.search(r'https?://(?:www\.)?github\.com/[^\s]+', resume_text)

    if linkedin_match:
        linkedin = linkedin_match.group()

    if github_match:
        github = github_match.group()

    return linkedin, github