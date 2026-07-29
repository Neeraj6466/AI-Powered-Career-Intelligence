from job_database import jobs

def recommend_jobs(user_skills):
    recommended_jobs = []

    # Convert user skills to lowercase for comparison
    user_skills = [skill.lower() for skill in user_skills]

    for job in jobs:
        matched_skills = []

        for skill in job["skills"]:
            if skill.lower() in user_skills:
                matched_skills.append(skill)

        if matched_skills:
            match_score = int((len(matched_skills) / len(job["skills"])) * 100)

            recommended_jobs.append({
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "salary": job["salary"],
                "skills": job["skills"],
                "matched_skills": matched_skills,
                "match_score": match_score,
                "apply": job["apply"]
            })

    # Sort jobs by highest match score
    recommended_jobs.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return recommended_jobs