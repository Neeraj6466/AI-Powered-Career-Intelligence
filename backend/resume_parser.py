import os
import PyPDF2
from docx import Document


def extract_text(file_path):

    text = ""

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".pdf":

        with open(file_path, "rb") as file:

            reader = PyPDF2.PdfReader(file)

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    elif file_extension == ".docx":

        document = Document(file_path)

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX resume.")

    return text