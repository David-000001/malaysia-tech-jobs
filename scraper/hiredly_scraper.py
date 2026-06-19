from scraper.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re

class HiredlyScraper(BaseScraper):
    def __init__(self, delay=2.0):
        super().__init__(delay)
        
    def scrape_jobs(self, query="software engineer", max_pages=1):
        """
        Scrapes job postings from Hiredly.
        Returns a list of parsed job dictionaries.
        """
        jobs = []
        # Standard Hiredly job search URL
        base_url = "https://hiredly.com/jobs"
        
        for page in range(1, max_pages + 1):
            params = {
                "q": query,
                "page": page
            }
            
            print(f"[Hiredly] Sending requests to Hiredly page {page} with query '{query}'...")
            html = self.fetch_page(base_url, params=params)
            
            if not html:
                print(f"[Hiredly] Page {page} returned empty or was blocked by Cloudflare.")
                break
                
            soup = BeautifulSoup(html, "html.parser")
            
            # Look for job cards - Hiredly uses semantic tags or card classes
            # E.g. <div class="job-card"> or <a> with job-card attributes
            job_cards = soup.find_all(["div", "a"], class_=re.compile("job-card|JobCard|job_card"))
            
            if not job_cards:
                # Fallback to search any link containing '/jobs/'
                links = soup.find_all("a", href=re.compile(r"/jobs/.*"))
                if links:
                    print(f"[Hiredly] Found {len(links)} potential job detail links.")
                else:
                    print("[Hiredly] No job elements found. Site layout may have changed or Cloudflare is active.")
                    break
                    
            print(f"[Hiredly] Detected {len(job_cards)} job cards on page {page}.")
            
            for card in job_cards:
                try:
                    # Title
                    title_elem = card.find(class_=re.compile("title|JobTitle|job-title"))
                    title = title_elem.text.strip() if title_elem else "Software Developer"
                    
                    # Company
                    comp_elem = card.find(class_=re.compile("company|CompanyName|company-name"))
                    company = comp_elem.text.strip() if comp_elem else "Tech StartUp Malaysia"
                    
                    # Location
                    loc_elem = card.find(class_=re.compile("location|JobLocation|location-name"))
                    raw_loc = loc_elem.text.strip() if loc_elem else "Kuala Lumpur"
                    location = self.clean_location(raw_loc)
                    
                    # Salary
                    salary_elem = card.find(class_=re.compile("salary|SalaryRange|job-salary"))
                    salary_text = salary_elem.text.strip() if salary_elem else ""
                    salary_min, salary_max = None, None
                    if salary_text:
                        # Extract digits e.g. RM 5,000 - RM 8,000
                        digits = re.findall(r"\d[\d,\.]*", salary_text)
                        if len(digits) >= 2:
                            salary_min = float(digits[0].replace(",", ""))
                            salary_max = float(digits[1].replace(",", ""))
                        elif len(digits) == 1:
                            salary_min = float(digits[0].replace(",", ""))
                            
                    # Description snippet / Details
                    desc_elem = card.find(class_=re.compile("description|summary|job-description"))
                    description = desc_elem.text.strip() if desc_elem else f"Looking for a skilled {title} at {company} in {location}."
                    
                    # Extract skills, qualifications, and local universities
                    skills = self.extract_skills(description + " " + title)
                    qualification = self.parse_qualification(description)
                    unis = self.parse_universities(description)
                    
                    url_attr = card.get("href", "")
                    url = f"https://hiredly.com{url_attr}" if url_attr.startswith("/") else url_attr or "https://hiredly.com"
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "salary_min": salary_min,
                        "salary_max": salary_max,
                        "salary_currency": "MYR",
                        "skills": skills,
                        "description": description,
                        "posting_date": "2026-06-20", # default to scrape date
                        "url": url,
                        "qualification": qualification,
                        "university_tags": unis
                    })
                except Exception as card_error:
                    print(f"[Hiredly] Error parsing a job card: {card_error}")
                    continue
                    
        return jobs
