from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()


def generate_report(filename, score, career, salary, skills, missing_skills, courses):

    doc = SimpleDocTemplate(filename)
    story = []

    story.append(Paragraph("<b>AI Career Intelligence Report</b>", styles["Heading1"]))
    story.append(Paragraph(f"<b>Resume Score:</b> {score}/100", styles["Normal"]))
    story.append(Paragraph(f"<b>Recommended Career:</b> {career}", styles["Normal"]))
    story.append(Paragraph(f"<b>Expected Salary:</b> {salary}", styles["Normal"]))

    story.append(Paragraph("<b>Skills Found</b>", styles["Heading2"]))
    for skill in skills:
        story.append(Paragraph(f"• {skill}", styles["Normal"]))

    story.append(Paragraph("<b>Missing Skills</b>", styles["Heading2"]))
    for skill in missing_skills:
        story.append(Paragraph(f"• {skill}", styles["Normal"]))

    story.append(Paragraph("<b>Recommended Courses</b>", styles["Heading2"]))
    for course in courses:
        story.append(Paragraph(f"• {course}", styles["Normal"]))

    doc.build(story)