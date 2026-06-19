import time
import random
import re
from datetime import datetime
from scraper.base_scraper import BaseScraper

MOCK_COMPANIES = [
    ("Setel", "Bangsar South, Kuala Lumpur"),
    ("Luno Malaysia", "KL Sentral, Kuala Lumpur"),
    ("Touch 'n Go eWallet", "Bangsar South, Kuala Lumpur"),
    ("Boost", "Mid Valley, Kuala Lumpur"),
    ("Mindvalley", "Kuala Lumpur"),
    ("ServiceRocket", "Petaling Jaya, Selangor"),
    ("Sitecore Malaysia", "KLCC, Kuala Lumpur"),
    ("Deriv", "Cyberjaya, Selangor"),
    ("TNG Digital", "Bangsar South, Kuala Lumpur"),
    ("Inari Amertron", "Shah Alam, Selangor"),
    ("Favco", "Puchong, Selangor")
]

MOCK_TITLES = [
    ("Python Developer", ["Python", "SQL", "Git", "Docker"], "Degree"),
    ("Senior React Engineer", ["React", "JavaScript", "Git", "AWS"], "Degree"),
    ("Node.js API Specialist", ["Node.js", "JavaScript", "SQL", "Git", "Docker"], "Diploma"),
    ("Laravel Web Developer", ["PHP", "Laravel", "SQL", "Git", "JavaScript"], "Diploma"),
    ("DevOps Cloud Engineer", ["AWS", "Docker", "Git", "Python"], "Degree"),
    ("Mobile Flutter Developer", ["Flutter", "Git", "JavaScript"], "Degree"),
    ("Android Developer (Kotlin)", ["Kotlin", "Git", "Java"], "Degree"),
    ("iOS Engineer (Swift)", ["Swift", "Git"], "Degree"),
    ("Systems Analyst (SAP)", ["SAP", "SQL", "Git"], "Not Specified"),
    ("Data Engineer", ["Python", "SQL", "Docker", "AWS", "Git"], "Master"),
    ("Junior Software Dev", ["PHP", "JavaScript", "SQL", "Git"], "SPM")
]

UNIVERSITIES = ["UM", "USM", "UKM", "UPM", "UTM", "UiTM", "Monash", "Taylor's", "Sunway", "MMU", "APU", "UTAR"]

class MockScraper(BaseScraper):
    def __init__(self, delay=1.0):
        super().__init__(delay)
        
    def scrape_jobs(self, query="developer", max_pages=1):
        """
        Simulates live scraping by generating realistic job listings.
        Includes console logs representing network jumps, rotation, and delays.
        """
        jobs = []
        print(f"[Simulator] Initializing live scraping simulation for query: '{query}'...")
        
        for page in range(1, max_pages + 1):
            # 1. Rotate User-Agent
            headers = self.get_headers()
            print(f"[Simulator] Rotated User-Agent to: '{headers['User-Agent']}'")
            
            # 2. Simulate Polite Delay
            sleep_time = self.delay + random.uniform(0.2, 0.8)
            print(f"[Simulator] Respecting robots.txt: Pausing for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
            
            # 3. Fetch log
            print(f"[Simulator] Fetching page {page} of results for '{query}'...")
            
            # 4. Generate random jobs matching the query
            num_jobs = random.randint(3, 5)
            print(f"[Simulator] HTML parsed successfully. Identified {num_jobs} listings on page {page}.")
            
            for i in range(num_jobs):
                company, location = random.choice(MOCK_COMPANIES)
                title, skills, qualification = random.choice(MOCK_TITLES)
                
                # Randomize salaries
                salary_min = float(random.randint(4, 12) * 1000)
                salary_max = salary_min + float(random.randint(2, 6) * 1000)
                
                # University mention
                uni = random.choice(UNIVERSITIES) if random.random() > 0.4 else ""
                uni_clause = f" Graduating from {uni} is a strong advantage." if uni else ""
                
                description = (
                    f"We are seeking a talented {title} to join our growing team at {company}. "
                    f"In this role, you will help design and maintain enterprise scale systems. "
                    f"Required technical skillsets include: {', '.join(skills)}.{uni_clause} "
                    f"Applicants should possess a {qualification} in Computer Science, Software Engineering or related field."
                )
                
                # Random posting date (within last 3 days)
                days_ago = random.randint(0, 3)
                post_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                
                url_slug = re.sub(r"[^a-zA-Z0-9]+", "-", f"{company}-{title}").lower()
                url = f"https://www.malaysiatechjobs.com.my/job/{url_slug}"
                
                job_id = f"mock-{url_slug}-{post_date}"
                
                jobs.append({
                    "id": job_id,
                    "title": f"{title} (Simulated)",
                    "company": company,
                    "location": location,
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "salary_currency": "MYR",
                    "skills": skills,
                    "description": description,
                    "posting_date": post_date,
                    "url": url,
                    "qualification": qualification,
                    "university_tags": [uni] if uni else []
                })
                print(f"  -> Extracted job: '{title}' at '{company}' in '{location}'")
                
        print(f"[Simulator] Scraping simulation complete. Successfully harvested {len(jobs)} postings.")
        return jobs
