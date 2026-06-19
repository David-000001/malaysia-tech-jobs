import os
import sqlite3
from datetime import datetime
import json

DEFAULT_DB_PATH = "jobs.db"

def get_db_path():
    """Retrieve database path from environment variable or default."""
    return os.environ.get("DB_PATH", DEFAULT_DB_PATH)

def get_db_connection(db_path=None):
    """Establish a connection to the SQLite database."""
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=None):
    """Create the tables if they don't exist and define indexes for performance."""
    if db_path is None:
        db_path = get_db_path()
        
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Create jobs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            salary_min REAL,
            salary_max REAL,
            salary_currency TEXT DEFAULT 'MYR',
            skills TEXT, -- Comma-separated skills
            description TEXT,
            posting_date TEXT, -- ISO Date format 'YYYY-MM-DD'
            url TEXT,
            qualification TEXT DEFAULT 'Not Specified',
            university_tags TEXT, -- Comma-separated list of universities
            scraped_at TEXT NOT NULL
        )
    """)
    
    # Indices for common filters
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_posting_date ON jobs(posting_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_qualification ON jobs(qualification)")
    
    conn.commit()
    conn.close()
    print(f"Database initialized at: {db_path}")

def save_jobs(jobs_list, db_path=None):
    """
    Saves a list of job dictionaries to the database.
    If a job with the same ID exists, it updates it.
    
    Each job in the list should be a dictionary containing:
    id, title, company, location, salary_min, salary_max, salary_currency,
    skills, description, posting_date, url, qualification, university_tags
    """
    if db_path is None:
        db_path = get_db_path()
        
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    inserted = 0
    updated = 0
    
    scraped_at = datetime.now().isoformat()
    
    for job in jobs_list:
        # Generate composite ID if not provided
        job_id = job.get("id")
        if not job_id:
            # Composite ID based on title, company, and location to prevent duplicates
            raw_id = f"{job.get('title')}-{job.get('company')}-{job.get('location')}"
            import hashlib
            job_id = hashlib.md5(raw_id.encode('utf-8')).hexdigest()
            
        # Ensure fields are structured correctly
        skills = job.get("skills", "")
        if isinstance(skills, list):
            skills = ",".join(skills)
            
        uni_tags = job.get("university_tags", "")
        if isinstance(uni_tags, list):
            uni_tags = ",".join(uni_tags)
            
        # Default qualification
        qualification = job.get("qualification", "Not Specified")
        
        # Check if job already exists
        cursor.execute("SELECT id FROM jobs WHERE id = ?", (job_id,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute("""
                UPDATE jobs SET
                    title = ?, company = ?, location = ?, salary_min = ?, salary_max = ?, 
                    salary_currency = ?, skills = ?, description = ?, posting_date = ?, 
                    url = ?, qualification = ?, university_tags = ?, scraped_at = ?
                WHERE id = ?
            """, (
                job.get("title"), job.get("company"), job.get("location"),
                job.get("salary_min"), job.get("salary_max"), job.get("salary_currency", "MYR"),
                skills, job.get("description"), job.get("posting_date"),
                job.get("url"), qualification, uni_tags, scraped_at, job_id
            ))
            updated += 1
        else:
            cursor.execute("""
                INSERT INTO jobs (
                    id, title, company, location, salary_min, salary_max, salary_currency,
                    skills, description, posting_date, url, qualification, university_tags, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id, job.get("title"), job.get("company"), job.get("location"),
                job.get("salary_min"), job.get("salary_max"), job.get("salary_currency", "MYR"),
                skills, job.get("description"), job.get("posting_date"),
                job.get("url"), qualification, uni_tags, scraped_at
            ))
            inserted += 1
            
    conn.commit()
    conn.close()
    return inserted, updated

def get_jobs(filters=None, db_path=None):
    """
    Fetch jobs from the database applying optional filters.
    filters can include: title, company, location, skill, min_salary, qualification, university
    """
    if db_path is None:
        db_path = get_db_path()
        
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []
    
    if filters:
        if filters.get("title"):
            query += " AND title LIKE ?"
            params.append(f"%{filters['title']}%")
        if filters.get("company"):
            query += " AND company LIKE ?"
            params.append(f"%{filters['company']}%")
        if filters.get("location"):
            query += " AND location LIKE ?"
            params.append(f"%{filters['location']}%")
        if filters.get("qualification") and filters.get("qualification") != "All":
            query += " AND qualification = ?"
            params.append(filters["qualification"])
        if filters.get("min_salary"):
            query += " AND salary_min >= ?"
            params.append(filters["min_salary"])
        if filters.get("skill"):
            query += " AND skills LIKE ?"
            params.append(f"%{filters['skill']}%")
        if filters.get("university"):
            query += " AND university_tags LIKE ?"
            params.append(f"%{filters['university']}%")
            
    # Order by posting date descending (most recent first)
    query += " ORDER BY posting_date DESC, scraped_at DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts
    jobs = []
    for row in rows:
        job = dict(row)
        # Parse skills and university tags back to lists
        job["skills"] = [s.strip() for s in job["skills"].split(",") if s.strip()] if job.get("skills") else []
        job["university_tags"] = [u.strip() for u in job["university_tags"].split(",") if u.strip()] if job.get("university_tags") else []
        jobs.append(job)
        
    return jobs

def get_db_stats(db_path=None):
    """Returns basic counts and statistics from the database."""
    if db_path is None:
        db_path = get_db_path()
        
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    stats = {}
    try:
        cursor.execute("SELECT COUNT(*) FROM jobs")
        stats["total_jobs"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT company) FROM jobs")
        stats["total_companies"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(salary_min) FROM jobs WHERE salary_min IS NOT NULL")
        stats["avg_min_salary"] = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT AVG(salary_max) FROM jobs WHERE salary_max IS NOT NULL")
        stats["avg_max_salary"] = cursor.fetchone()[0] or 0.0
    except Exception as e:
        print(f"Error getting DB stats: {e}")
        stats = {"total_jobs": 0, "total_companies": 0, "avg_min_salary": 0.0, "avg_max_salary": 0.0}
    finally:
        conn.close()
        
    return stats
