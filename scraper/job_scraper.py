"""
NYC Jobs scraper.

This module is responsible for:
- Starting Selenium
- Opening NYC Jobs pages
- Parsing job listings
- Extracting basic job-posting information

Filtering and detailed job analysis are handled by the
analysis package.
"""

import platform
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def kill_zombie_drivers():
    """
    Attempt to close leftover Chrome/ChromeDriver processes.

    This is primarily useful when previous Selenium sessions
    did not close correctly.
    """
    try:
        if platform.system() == "Windows":
            import subprocess

            subprocess.run(
                ["taskkill", "/F", "/IM", "chromedriver.exe"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            subprocess.run(
                ["taskkill", "/F", "/IM", "chrome.exe"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        elif platform.system() in ("Linux", "Darwin"):
            import subprocess

            subprocess.run(
                ["pkill", "-f", "chromedriver"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    except Exception:
        # Process cleanup is optional and should not stop the scraper.
        pass


def create_driver(headless=False):
    """
    Create and configure a Selenium Chrome WebDriver.
    """
    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")

    # Faster page loading.
    options.page_load_strategy = "eager"

    driver = webdriver.Chrome(options=options)

    return driver


def build_paged_url(base_url, page_number):
    """
    Build the URL for a specific NYC Jobs results page.

    Parameters
    ----------
    base_url : str
        Original NYC Jobs search URL.

    page_number : int
        Page number to retrieve.

    Returns
    -------
    str
        URL for the requested page.
    """
    if page_number <= 1:
        return base_url

    separator = "&" if "?" in base_url else "?"

    return f"{base_url}{separator}page={page_number}"


def extract_job_listings(html):
    """
    Parse an NYC Jobs results page and extract basic job information.

    Returns
    -------
    list
        List of dictionaries containing job information.
    """
    soup = BeautifulSoup(html, "html.parser")

    jobs = []

    # ---------------------------------------------------------
    # Locate job links/cards
    # ---------------------------------------------------------
    #
    # Keep the selectors based on the actual NYC Jobs page
    # structure used by your working scraper.
    #

    job_links = soup.find_all("a", href=True)

    for link in job_links:
        title = link.get_text(" ", strip=True)
        href = link.get("href", "")

        if not title or not href:
            continue

        # Skip obvious navigation/UI links.
        if len(title) < 3:
            continue

        if not any(
            keyword in title.lower()
            for keyword in [
                "analyst",
                "finance",
                "financial",
                "credit",
                "loan",
                "lending",
                "banking",
                "business",
                "accounting",
                "budget",
                "procurement",
            ]
        ):
            continue

        jobs.append(
            {
                "job_title": title,
                "job_url": href,
            }
        )

    return jobs


def scrape_job_page(driver, url):
    """
    Open a single job page and extract its visible text.
    """
    try:
        driver.get(url)

        time.sleep(1)

        soup = BeautifulSoup(
            driver.page_source,
            "html.parser"
        )

        return soup.get_text("\n", strip=True)

    except Exception:
        return ""


def scrape_job_board(
    base_url,
    pages=5,
    headless=False,
):
    """
    Scrape multiple pages of NYC Jobs listings.

    Parameters
    ----------
    base_url : str
        NYC Jobs search URL.

    pages : int
        Number of result pages to scrape.

    headless : bool
        Whether Chrome should run without a visible window.

    Returns
    -------
    list
        Raw job postings.
    """

    kill_zombie_drivers()

    driver = create_driver(headless=headless)

    jobs = []

    try:
        for page_number in range(1, pages + 1):

            page_url = build_paged_url(
                base_url,
                page_number
            )

            try:
                driver.get(page_url)

                # Wait until links are available.
                try:
                    driver.find_element(
                        By.TAG_NAME,
                        "a"
                    )
                except Exception:
                    pass

                time.sleep(1)

                page_jobs = extract_job_listings(
                    driver.page_source
                )

                for job in page_jobs:
                    job["search_url"] = base_url

                jobs.extend(page_jobs)

            except Exception as e:
                print(
                    f"Error scraping page "
                    f"{page_number}: {e}"
                )

    finally:
        driver.quit()

    return jobs
