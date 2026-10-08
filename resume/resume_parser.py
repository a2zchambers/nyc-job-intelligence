```python
"""
Resume parsing and validation.

This module handles:
- Extracting text from PDF resumes
- Extracting text from DOCX resumes
- Validating that an uploaded file appears to be a resume
- Extracting relevant competencies from the resume

The parser does not generate or modify the resume.
"""

import io
import re

from docx import Document
from pypdf import PdfReader

from analysis.keyword_lists import COMMON_SKILLS


def extract_pdf_text(file):
    """
    Extract text from an uploaded PDF resume.

    Parameters
    ----------
    file
        Uploaded Streamlit file object.

    Returns
    -------
    str
        Extracted text from the PDF.
    """
    try:
        file_bytes = file.read()
        reader = PdfReader(io.BytesIO(file_bytes))

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n".join(pages).strip()

    except Exception as e:
        raise ValueError(f"Could not read PDF resume: {e}")


def extract_docx_text(file):
    """
    Extract text from an uploaded DOCX resume.

    Parameters
    ----------
    file
        Uploaded Streamlit file object.

    Returns
    -------
    str
        Extracted text from the DOCX file.
    """
    try:
        file_bytes = file.read()
        document = Document(io.BytesIO(file_bytes))

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs).strip()

    except Exception as e:
        raise ValueError(f"Could not read DOCX resume: {e}")


def extract_resume_text(file):
    """
    Extract text from a supported resume file.

    Supported formats:
    - PDF
    - DOCX
    """
    if file is None:
        raise ValueError("No resume file was provided.")

    filename = file.name.lower()

    if filename.endswith(".pdf"):
        return extract_pdf_text(file)

    if filename.endswith(".docx"):
        return extract_docx_text(file)

    raise ValueError(
        "Unsupported file type. Please upload a PDF or DOCX resume."
    )


def clean_resume_text(resume_text):
    """
    Clean extracted resume text while preserving useful line breaks.
    """
    if not resume_text:
        return ""

    # Normalize Windows/Mac line endings.
    resume_text = resume_text.replace("\r\n", "\n")
    resume_text = resume_text.replace("\r", "\n")

    # Remove excessive spaces.
    resume_text = re.sub(r"[ \t]+", " ", resume_text)

    # Remove excessive blank lines.
    resume_text = re.sub(r"\n{3,}", "\n\n", resume_text)

    return resume_text.strip()


def validate_resume_text(resume_text):
    """
    Check whether extracted text appears to be a resume.

    Returns
    -------
    tuple
        (is_valid, message)
    """
    if not resume_text:
        return False, "No text could be extracted from the file."

    if len(resume_text.strip()) < 100:
        return False, "The uploaded file contains too little text to be a resume."

    resume_lower = resume_text.lower()

    resume_indicators = [
        "experience",
        "education",
        "skills",
        "employment",
        "work experience",
        "professional experience",
        "university",
        "college",
        "degree",
        "bachelor",
        "master",
        "certification",
    ]

    matches = sum(
        1
        for indicator in resume_indicators
        if indicator in resume_lower
    )

    if matches < 2:
        return False, "The uploaded file does not appear to be a resume."

    return True, "Resume successfully validated."


def extract_resume_competencies(resume_text):
    """
    Identify competencies from the resume using the project's
    centralized keyword list.

    This is rule-based keyword matching, not an LLM analysis.
    """
    if not resume_text:
        return []

    resume_lower = resume_text.lower()
    competencies = []

    for skill in COMMON_SKILLS:
        if skill.lower() in resume_lower:
            competencies.append(skill)

    return list(dict.fromkeys(competencies))


def parse_resume(file):
    """
    Complete resume parsing pipeline.

    Returns
    -------
    dict
        Parsed resume information containing:
        - text
        - competencies
        - filename
    """
    resume_text = extract_resume_text(file)
    resume_text = clean_resume_text(resume_text)

    is_valid, message = validate_resume_text(resume_text)

    if not is_valid:
        raise ValueError(message)

    competencies = extract_resume_competencies(resume_text)

    return {
        "filename": file.name,
        "text": resume_text,
        "competencies": competencies,
    }
