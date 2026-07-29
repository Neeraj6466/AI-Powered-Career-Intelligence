def generate_roadmap(missing_skills):

    roadmap = []

    week = 1

    for skill in missing_skills:

        roadmap.append(f"Week {week}: Learn {skill}")

        week += 1

    roadmap.append(f"Week {week}: Build a Mini Project")

    roadmap.append(f"Week {week+1}: Practice Interview Questions")

    roadmap.append(f"Week {week+2}: Apply for Internships")

    return roadmap