```python
import sqlite3
from datetime import datetime


DB_FILE = "jobs_batch.db"
TABLE_NAME = "batch_jobs_v16"


def get_connection():
    """
    Create and return a connection to the SQLite database.
    """
    return sqlite3.connect(DB_FILE)


def init_db():
    """
    Create the jobs table if it does not already exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_url TEXT,
            job_url TEXT UNIQUE,
            job_title TEXT,
            agency TEXT,
            salary TEXT,
            location TEXT,
            category TEXT,
            description TEXT,
            min_qualifications TEXT,
            preferred_qualifications TEXT,
            preferred_skills TEXT,
            ats_keywords TEXT,
            posted_until TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_jobs_batch(jobs):
    """
    Save a list of job postings to the database.

    Existing jobs with the same job URL are ignored.
    """
    if not jobs:
        return

    conn = get_connection()
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for job in jobs:
        cursor.execute(
            f"""
            INSERT OR IGNORE INTO {TABLE_NAME} (
                search_url,
                job_url,
                job_title,
                agency,
                salary,
                location,
                category,
                description,
                min_qualifications,
                preferred_qualifications,
                preferred_skills,
                ats_keywords,
                posted_until,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job.get("search_url", ""),
                job.get("job_url", ""),
                job.get("job_title", ""),
                job.get("agency", ""),
                job.get("salary", ""),
                job.get("location", ""),
                job.get("category", ""),
                job.get("description", ""),
                job.get("min_qualifications", ""),
                job.get("preferred_qualifications", ""),
                job.get("preferred_skills", ""),
                job.get("ats_keywords", ""),
                job.get("posted_until", ""),
                timestamp,
            ),
        )

    conn.commit()
    conn.close()


def get_saved_jobs():
    """
    Retrieve all saved jobs from the database.
    """
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT
            search_url,
            job_url,
            job_title,
            agency,
            salary,
            location,
            category,
            description,
            min_qualifications,
            preferred_qualifications,
            preferred_skills,
            ats_keywords,
            posted_until,
            timestamp
        FROM {TABLE_NAME}
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def delete_all_jobs():
    """
    Delete all saved jobs from the database.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"DELETE FROM {TABLE_NAME}")

    conn.commit()
    conn.close()
