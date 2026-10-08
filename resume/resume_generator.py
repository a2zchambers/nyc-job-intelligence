```python
"""
Resume generation logic.

This module takes the user's resume information and a job posting
and creates a tailored resume based on the job's ATS keywords.

The current version uses a rule-based/template approach.
It does not make an LLM/Ollama call.
"""


def generate_tailored_resume(
    job,
    resume_data,
    ats_keywords=None
):
    """
    Generate a tailored resume for a specific job.

    Parameters
    ----------
    job : dict
        Information extracted from the selected job posting.

    resume_data : dict
        Information extracted from the user's uploaded resume.

    ats_keywords : list, optional
        Keywords identified as relevant to the job posting.

    Returns
    -------
    str
        Resume content formatted as Markdown.
    """

    ats_keywords = ats_keywords or []

    # ---------------------------------------------------------
    # User information
    # ---------------------------------------------------------

    name = resume_data.get("name", "")
    email = resume_data.get("email", "")
    phone = resume_data.get("phone", "")
    location = resume_data.get("location", "")
    linkedin = resume_data.get("linkedin", "")

    # ---------------------------------------------------------
    # Resume sections
    # ---------------------------------------------------------

    education = resume_data.get("education", "")
    experience = resume_data.get("experience", "")
    skills = resume_data.get("skills", "")

    # ---------------------------------------------------------
    # Job information
    # ---------------------------------------------------------

    job_title = job.get("job_title", "")
    agency = job.get("agency", "")

    # ---------------------------------------------------------
    # ATS keywords
    # ---------------------------------------------------------

    if ats_keywords:
        ats_keyword_text = ", ".join(ats_keywords)
    else:
        ats_keyword_text = ""

    # ---------------------------------------------------------
    # Build resume
    # ---------------------------------------------------------

    resume = f"""# {name}

{location} | {phone} | {email} | {linkedin}

## PROFESSIONAL EXPERIENCE

{experience}

## EDUCATION

{education}

## SKILLS

{skills}
"""

    # Add relevant keywords only when they are actually
    # supported by the user's resume.
    if ats_keyword_text:
        resume += f"""
## RELEVANT KEYWORDS

{ats_keyword_text}
"""

    return resume


def tailor_resume_to_job(job, resume_data):
    """
    Generate a resume using the ATS keywords associated
    with a specific job posting.
    """

    ats_keywords = job.get("ats_keywords", [])

    # Database values may be stored as a string rather than
    # a Python list.
    if isinstance(ats_keywords, str):
        ats_keywords = [
            keyword.strip()
            for keyword in ats_keywords.split(",")
            if keyword.strip()
        ]

    return generate_tailored_resume(
        job=job,
        resume_data=resume_data,
        ats_keywords=ats_keywords
    )
