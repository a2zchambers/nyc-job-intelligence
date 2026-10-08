"""
Resume generation logic.

This module creates a tailored resume from the user's uploaded
master resume and information extracted from a job posting.

Important:
- The user's resume is the source of truth.
- Job-specific keywords can be incorporated when they accurately
  match the user's existing experience or skills.
- The generator should not invent employers, job titles,
  responsibilities, education, certifications, or metrics.
"""

import re


def clean_resume_text(resume_text):
    """
    Clean the uploaded resume text before using it to generate
    a tailored resume.
    """
    if not resume_text:
        return ""

    # Remove excessive whitespace while preserving line breaks.
    resume_text = re.sub(r"[ \t]+", " ", resume_text)
    resume_text = re.sub(r"\n{3,}", "\n\n", resume_text)

    return resume_text.strip()


def find_matching_keywords(resume_text, ats_keywords):
    """
    Find ATS keywords from the job posting that already appear
    in the user's resume.

    Only keywords already supported by the user's resume are
    returned. This helps prevent unsupported claims.
    """
    if not resume_text or not ats_keywords:
        return []

    resume_lower = resume_text.lower()
    matching_keywords = []

    for keyword in ats_keywords:
        if keyword and keyword.lower() in resume_lower:
            matching_keywords.append(keyword)

    return list(dict.fromkeys(matching_keywords))


def build_resume_prompt(
    resume_text,
    job_title,
    agency,
    job_description,
    ats_keywords=None,
):
    """
    Build the prompt used by an LLM to tailor the user's resume.

    The prompt explicitly prevents the model from inventing
    experience or qualifications.
    """
    resume_text = clean_resume_text(resume_text)

    ats_keywords = ats_keywords or []

    matching_keywords = find_matching_keywords(
        resume_text,
        ats_keywords
    )

    keyword_text = ", ".join(matching_keywords)

    prompt = f"""
You are helping tailor a resume for a job application.

SOURCE RESUME:
{resume_text}

TARGET JOB:
Job Title: {job_title}
Agency/Organization: {agency}

JOB DESCRIPTION:
{job_description}

ATS KEYWORDS THAT ALREADY APPEAR IN THE RESUME:
{keyword_text}

Instructions:

1. Use the source resume as the only source of truth.
2. Do not invent employers, job titles, responsibilities,
   education, certifications, technical skills, or achievements.
3. Do not create statistics or performance metrics that are not
   present in the source resume.
4. Do not claim experience with a technology, financial product,
   software, or process unless the source resume supports it.
5. Prioritize experience and skills that are relevant to the
   target job.
6. Use relevant ATS terminology when it accurately describes
   experience already present in the source resume.
7. Keep the resume concise and professional.
8. Preserve the candidate's actual employment history and
   education.
9. If a job requirement is not supported by the source resume,
   do not pretend that the candidate has it.
10. Do not add a professional summary unless specifically requested.

Return only the tailored resume text.
"""

    return prompt


def generate_resume_content(
    resume_text,
    job_title,
    agency,
    job_description,
    ats_keywords=None,
    llm=None,
):
    """
    Generate tailored resume content.

    Parameters
    ----------
    resume_text : str
        Text extracted from the user's uploaded master resume.

    job_title : str
        Target job title.

    agency : str
        Target agency or organization.

    job_description : str
        Full target job description.

    ats_keywords : list
        Keywords extracted from the job posting.

    llm : optional
        LLM object used to generate the tailored resume.

    Returns
    -------
    str
        Tailored resume text.
    """

    prompt = build_resume_prompt(
        resume_text=resume_text,
        job_title=job_title,
        agency=agency,
        job_description=job_description,
        ats_keywords=ats_keywords,
    )

    if llm is None:
        # Without an LLM, return the original resume rather than
        # creating unsupported information.
        return clean_resume_text(resume_text)

    response = llm.invoke(prompt)

    if hasattr(response, "content"):
        response = response.content

    return str(response).strip()
