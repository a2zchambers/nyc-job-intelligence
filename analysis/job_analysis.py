import r


def extract_posted_until(description):
    """
    Extract the job posting's closing date from the description.
    """
    if not description:
        return "Not listed"

    patterns = [
        r"POSTED UNTIL:\s*(.*?)(?:\n|$)",
        r"POST UNTIL:\s*(.*?)(?:\n|$)",
        r"DEADLINE:\s*(.*?)(?:\n|$)",
        r"CLOSING DATE:\s*(.*?)(?:\n|$)"
    ]

    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return "Not listed"


def extract_highlighted_qualifications(description):
    """
    Extract minimum and preferred qualifications
    from the job description.
    """
    if not description:
        return {
            "minimum": "Not listed",
            "preferred": "Not listed"
        }

    # Put your current qualification-extraction logic here.
    # Keep the function focused on extracting qualifications.
    
    return {
        "minimum": "Not listed",
        "preferred": "Not listed"
    }


def extract_preferred_skills(description):
    """
    Extract preferred skills mentioned in the job posting.
    """
    if not description:
        return []

    # Put your current preferred-skills logic here.
    return []


def generate_ats_keywords(job_text, resume_competencies):
    """
    Identify ATS keywords that overlap between the
    job posting and the user's resume competencies.
    """
    if not job_text:
        return []

    job_text_lower = job_text.lower()

    keywords = []

    for competency in resume_competencies:
        if competency.lower() in job_text_lower:
            keywords.append(competency)

    return list(dict.fromkeys(keywords))
