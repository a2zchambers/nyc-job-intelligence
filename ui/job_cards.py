"""
NYC Jobs card parsing.

This module extracts individual job listings from the HTML
returned by the NYC Jobs search-results pages.

It does not:
- Start Selenium
- Filter jobs
- Analyze qualifications
- Access the database
- Generate resumes

Those responsibilities belong to other modules.
"""

from urllib.parse import urljoin


# Base URL used when NYC Jobs returns relative links.
NYC_JOBS_BASE_URL = "https://cityjobs.nyc.gov"


def clean_text(text):
    """
    Clean text extracted from an HTML element.
    """
    if not text:
        return ""

    return " ".join(text.split()).strip()


def extract_job_cards(soup):
    """
    Find individual job cards/listings on an NYC Jobs
    search-results page.

    Parameters
    ----------
    soup : BeautifulSoup
        Parsed HTML from the search-results page.

    Returns
    -------
    list
        List of raw job-card dictionaries.
    """

    jobs = []

    # ---------------------------------------------------------
    # Use the actual NYC Jobs card selector from the working
    # scraper here.
    # ---------------------------------------------------------
    #
    # The exact HTML structure of the website can change, so
    # this selector should match the structure you tested.
    #

    cards = soup.select("a")

    for card in cards:

        title = clean_text(card.get_text(" ", strip=True))
        href = card.get("href", "")

        if not title or not href:
            continue

        # Ignore extremely short links that are unlikely
        # to represent a job posting.
        if len(title) < 3:
            continue

        # Convert relative NYC Jobs URLs into full URLs.
        job_url = urljoin(
            NYC_JOBS_BASE_URL,
            href
        )

        jobs.append(
            {
                "job_title": title,
                "job_url": job_url,
            }
        )

    return jobs


def deduplicate_job_cards(jobs):
    """
    Remove duplicate job cards based on job URL.
    """
    unique_jobs = []
    seen_urls = set()

    for job in jobs:
        job_url = job.get("job_url", "")

        if not job_url:
            continue

        if job_url in seen_urls:
            continue

        seen_urls.add(job_url)
        unique_jobs.append(job)

    return unique_jobs


def parse_job_cards(soup):
    """
    Complete job-card parsing pipeline.

    Returns a clean list of unique job postings.
    """
    jobs = extract_job_cards(soup)

    jobs = deduplicate_job_cards(jobs)

    return jobs
