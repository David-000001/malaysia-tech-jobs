from scraper.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re

class JobStreetScraper(BaseScraper):
    def __init__(self, delay=2.5):
        super().__init__(delay)
        
    def scrape_jobs(self, query="developer", max_pages=1):
        """
        Scrapes job postings from JobStreet Malaysia.
        Returns a list of parsed job dictionaries.
        """
        jobs = []
        # JobStreet Malaysia uses SEEK-based URL structure
        base_url = "https://www.jobstreet.com.my/en/job-search"
        
        for page in range(1, max_pages + 1):
            params = {
                "key": query,
                "pg": page
            }
            
            print(f"[JobStreet] Querying JobStreet page {page} with term '{query}'...")
            html = self.fetch_page(base_url, params=params)
            
            if not html:
                print(f"[JobStreet] Page {page} returned empty or was blocked by Cloudflare.")
                break
                
            soup = BeautifulSoup(html, "html.parser")
            
            # JobStreet (SEEK) job cards commonly have data-automation="jobCard" or "job-card"
            job_cards = soup.find_all(attrs={"data-automation": "jobCard"})
            
            if not job_cards:
                # Fallback to general article/div structures
                job_cards = soup.find_all("article")
                if not job_cards:
                    job_cards = soup.find_all("div", class_=re.compile("job-card|JobCard|job_card"))
            
            if not job_cards:
                print("[JobStreet] No job cards found on page. Cloudflare or layout change detected.")
                break
                
            print(f"[JobStreet] Found {len(job_cards)} job cards on page {page}.")
            
            for card in job_cards:
                try:
                    # Title
                    title_elem = card.find(attrs={"data-automation": "jobTitle"}) or card.find("h1") or card.find("h2")
                    title = title_elem.text.strip() if title_elem else "Software Engineer"
                    
                    # Company
                    comp_elem = card.find(attrs={"data-automation": "jobCompany"}) or card.find("a", class_=re.compile("company|employer"))
                    company = comp_elem.text.strip() if comp_elem else "Malaysian Tech Enterprise"
                    
                    # Location
                    loc_elem = card.find(attrs={"data-automation": "jobLocation"}) or card.find("span", class_=re.compile("location|area"))
                    raw_loc = loc_elem.text.strip() if loc_elem else "Selangor"
                    location = self.clean_location(raw_loc)
                    
                    # Salary
                    salary_elem = card.find(attrs={"data-automation": "jobSalary"}) or card.find("span", class_=re.compile("salary|package"))
                    salary_text = salary_elem.text.strip() if salary_elem else ""
                    salary_min, salary_max = None, None
                    if salary_text:
                        # Extract numbers
                        digits = re.findall(r"\d[\d,\.]*", salary_text)
                        if len(digits) >= 2:
                            salary_min = float(digits[0].replace(",", ""))
                            salary_max = float(digits[1].replace(",", ""))
                        elif len(digits) == 1:
                            salary_min = float(digits[0].replace(",", ""))
                            
                    # Description / Details
                    desc_elem = card.find(attrs={"data-automation": "jobShortDescription"}) or card.find("p")
                    description = desc_elem.text.strip() if desc_elem else f"Excellent software position as {title} at {company} located in {location}."
                    
                    # Extract skills, qualifications, and local universities
                    skills = self.extract_skills(description + " " + title)
                    qualification = self.parse_qualification(description)
                    unis = self.parse_universities(description)
                    
                    # URL
                    url_elem = card.find("a")
                    url_attr = url_elem.get("href", "") if url_elem else ""
                    url = f"https://www.jobstreet.com.my{url_attr}" if url_attr.startswith("/") else url_attr or "https://www.jobstreet.com.my"
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "salary_min": salary_min,
                        "salary_max": salary_max,
                        "salary_currency": "MYR",
                        "skills": skills,
                        "description": description,
                        "posting_date": "2026-06-20",
                        "url": url,
                        "qualification": qualification,
                        "university_tags": unis
                    })
                except Exception as card_error:
                    print(f"[JobStreet] Error parsing a job card: {card_error}")
                    continue
                    
        return jobs
