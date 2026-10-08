import r


def is_job_strictly_relevant(job_title, description, resume_competencies):
    """
    Determine whether a job posting is relevant to the user's
    background and search criteria.

    The function uses rule-based filtering rather than an LLM.
    """

    if not job_title and not description:
        return False

    title = job_title or ""
    text = f"{title} {description or ''}".lower()

    # ---------------------------------------------------------
    # 1. Remove obvious UI / website noise
    # ---------------------------------------------------------

    noise_keywords = [
        "sign in",
        "login",
        "create account",
        "save job",
        "share",
        "apply now",
        "search jobs",
    ]

    if any(keyword in text for keyword in noise_keywords):
        # Don't automatically reject the job just because
        # one of these appears. These terms can exist in
        # legitimate scraped page content.
        pass

    # ---------------------------------------------------------
    # 2. Reject jobs that are above the intended seniority
    # ---------------------------------------------------------

    negative_keywords = [
        "senior",
        "manager",
        "director",
        "supervisor",
        "lead",
        "executive",
        "chief",
        "vice president",
        "vp",
    ]

    title_lower = title.lower()

    if any(
        re.search(rf"\b{re.escape(keyword)}\b", title_lower)
        for keyword in negative_keywords
    ):
        return False

    # ---------------------------------------------------------
    # 3. Look for relevant finance / business keywords
    # ---------------------------------------------------------

    positive_anchors = [
        "finance",
        "financial",
        "credit",
        "underwriting",
        "banking",
        "loan",
        "lending",
        "commercial",
        "analyst",
        "risk",
        "investment",
        "accounting",
        "budget",
        "procurement",
        "business",
    ]

    has_positive_anchor = any(
        re.search(rf"\b{re.escape(keyword)}\b", text)
        for keyword in positive_anchors
    )

    if not has_positive_anchor:
        return False

    # ---------------------------------------------------------
    # 4. Compare against resume competencies
    # ---------------------------------------------------------

    if resume_competencies:
        competency_matches = sum(
            1
            for competency in resume_competencies
            if competency.lower() in text
        )

        # Keep jobs with at least one meaningful connection
        # to the user's background.
        if competency_matches == 0:
            return False

    return True
