import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to allow importing database module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.connection import init_db, save_jobs, get_db_stats

# Realistic Malaysian Tech Job Listings for Seeding
SEED_JOBS = [
    {
        "title": "Senior Backend Engineer (Python)",
        "company": "Grab Malaysia",
        "location": "Bangsar South, Kuala Lumpur",
        "salary_min": 12000.0,
        "salary_max": 18000.0,
        "salary_currency": "MYR",
        "skills": ["Python", "SQL", "Docker", "Git", "AWS"],
        "description": "Grab is Southeast Asia's leading superapp. We are looking for a Senior Backend Engineer to design high-throughput microservices. Candidates should have a Degree in Computer Science or Software Engineering from reputable universities such as UM or Monash Malaysia. Deep knowledge of Python, SQL, Docker, and AWS is required.",
        "posting_date": "2026-06-18",
        "url": "https://www.grab.careers/jobs/sr-backend-python",
        "qualification": "Degree",
        "university_tags": "UM, Monash"
    },
    {
        "title": "Frontend Developer (React)",
        "company": "Carsome",
        "location": "Mutiara Damansara, Selangor",
        "salary_min": 6000.0,
        "salary_max": 9500.0,
        "salary_currency": "MYR",
        "skills": ["React", "JavaScript", "Git", "Node.js"],
        "description": "Carsome is Southeast Asia's largest integrated car e-commerce platform. Join our team to build next-generation web apps using React and modern JavaScript. Diploma or Degree in IT is required. Experience with Git version control and Node.js backend integration is a plus. APU or UTAR graduates are encouraged to apply.",
        "posting_date": "2026-06-15",
        "url": "https://careers.carsome.com/jobs/react-frontend",
        "qualification": "Degree",
        "university_tags": "APU, UTAR"
    },
    {
        "title": "Full Stack PHP Engineer",
        "company": "Juris Technologies",
        "location": "Bangsar South, Kuala Lumpur",
        "salary_min": 5000.0,
        "salary_max": 8000.0,
        "salary_currency": "MYR",
        "skills": ["PHP", "Laravel", "JavaScript", "SQL", "Git"],
        "description": "Juris Tech is a leading Malaysian fintech company. We are looking for a software engineer proficient in PHP and Laravel framework. Must be able to write SQL queries and manage Git repos. Diploma holder or STPM with relevant coding experience will be considered. Prefer graduates from USM or MMU.",
        "posting_date": "2026-06-12",
        "url": "https://www.juristech.net/careers/full-stack-php",
        "qualification": "Diploma",
        "university_tags": "USM, MMU"
    },
    {
        "title": "Cloud DevOps Engineer",
        "company": "Aerodyne Group",
        "location": "Cyberjaya, Selangor",
        "salary_min": 9000.0,
        "salary_max": 14000.0,
        "salary_currency": "MYR",
        "skills": ["AWS", "Docker", "Git", "Python"],
        "description": "Aerodyne is a DT3 (Drone Tech, Data Tech, and Digital Transformation) drone enterprise solution provider. We need a DevOps engineer to automate our cloud pipelines. Experience in AWS, Docker, Git, and Python script automation is vital. Degree in Computer Science from UTM or Taylor's is preferred.",
        "posting_date": "2026-06-08",
        "url": "https://aerodyne.group/careers/devops",
        "qualification": "Degree",
        "university_tags": "UTM, Taylor's"
    },
    {
        "title": "Data Scientist",
        "company": "MoneyLion Malaysia",
        "location": "KL Sentral, Kuala Lumpur",
        "salary_min": 10000.0,
        "salary_max": 16000.0,
        "salary_currency": "MYR",
        "skills": ["Python", "SQL", "Git", "AWS"],
        "description": "MoneyLion is a mobile finance platform. We are seeking a Data Scientist to build credit rating ML models. Candidate must have a Master or PhD degree, ideally from UM or USM. Solid foundation in Python, SQL, Git, and data mining tools is required.",
        "posting_date": "2026-06-05",
        "url": "https://www.moneylion.com/careers/data-scientist",
        "qualification": "Master",
        "university_tags": "UM, USM"
    },
    {
        "title": "Junior Web Developer (PHP/JS)",
        "company": "Photobook Worldwide",
        "location": "Petaling Jaya, Selangor",
        "salary_min": 3500.0,
        "salary_max": 5000.0,
        "salary_currency": "MYR",
        "skills": ["PHP", "JavaScript", "SQL", "Git"],
        "description": "Photobook is looking for a junior developer. Learn to build and scale photo-printing e-commerce platforms. SPM or STPM graduates with a strong programming portfolio are welcome to apply. Technical stack: PHP, JavaScript, SQL, Git.",
        "posting_date": "2026-05-28",
        "url": "https://www.photobookworldwide.com/careers/jr-web-dev",
        "qualification": "SPM",
        "university_tags": ""
    },
    {
        "title": "Systems Administrator (SAP/SQL)",
        "company": "Maxis",
        "location": "KLCC, Kuala Lumpur",
        "salary_min": 8000.0,
        "salary_max": 12000.0,
        "salary_currency": "MYR",
        "skills": ["SAP", "SQL", "Git"],
        "description": "Maxis is a leading communications service provider in Malaysia. We require a Systems Administrator to maintain our enterprise SAP modules and SQL databases. A Degree or Diploma in IT/IS is required. Experience with Git is preferred. UKM or UPM graduates will be prioritized.",
        "posting_date": "2026-05-20",
        "url": "https://www.maxis.com.my/careers/sap-sys-admin",
        "qualification": "Degree",
        "university_tags": "UKM, UPM"
    },
    {
        "title": "Software Engineer (Java/SQL)",
        "company": "Maybank",
        "location": "KL Sentral, Kuala Lumpur",
        "salary_min": 6500.0,
        "salary_max": 10500.0,
        "salary_currency": "MYR",
        "skills": ["Java", "SQL", "Git"],
        "description": "Maybank is Malaysia's largest bank. Join our digital banking squad. You will develop backend services using Java, SQL databases, and Git. Degree in Software Engineering or Computer Science from UM, UTM, or Sunway is required.",
        "posting_date": "2026-05-15",
        "url": "https://maybank.com/careers/java-developer",
        "qualification": "Degree",
        "university_tags": "UM, UTM, Sunway"
    },
    {
        "title": "Senior React Native Engineer",
        "company": "Grab Malaysia",
        "location": "Mid Valley, Kuala Lumpur",
        "salary_min": 11000.0,
        "salary_max": 17000.0,
        "salary_currency": "MYR",
        "skills": ["React", "JavaScript", "Git", "Docker"],
        "description": "Work in our consumer platform team. Develop robust mobile layouts with React Native and JavaScript. Requires a Degree from a top university such as Monash, Taylor's or UM. Docker knowledge and Git workflow proficiency are mandatory.",
        "posting_date": "2026-05-10",
        "url": "https://www.grab.careers/jobs/react-native-mobi",
        "qualification": "Degree",
        "university_tags": "Monash, Taylor's, UM"
    },
    {
        "title": "Database Engineer (SQL/AWS)",
        "company": "Carsome",
        "location": "Mutiara Damansara, Selangor",
        "salary_min": 7000.0,
        "salary_max": 11000.0,
        "salary_currency": "MYR",
        "skills": ["SQL", "AWS", "Git", "Python"],
        "description": "Carsome needs a Database Engineer. Optimize SQL performance and manage database backups on AWS. Degree or Diploma in Data Analytics or CS. Git and Python automation skills are highly valued. APU, UTAR, or UiTM alumni are welcome.",
        "posting_date": "2026-04-25",
        "url": "https://careers.carsome.com/jobs/db-engineer",
        "qualification": "Degree",
        "university_tags": "APU, UTAR, UiTM"
    },
    {
        "title": "Cloud Architect (AWS)",
        "company": "Aerodyne Group",
        "location": "Cyberjaya, Selangor",
        "salary_min": 13000.0,
        "salary_max": 20000.0,
        "salary_currency": "MYR",
        "skills": ["AWS", "Docker", "Python", "Git"],
        "description": "Design and architect next-generation containerized drone-data storage pipelines on AWS. Requires a Master or PhD. Must have extensive experience in AWS, Docker, Python scripting, and Git processes.",
        "posting_date": "2026-04-18",
        "url": "https://aerodyne.group/careers/cloud-architect",
        "qualification": "Master",
        "university_tags": ""
    },
    {
        "title": "QA Automation Engineer",
        "company": "MoneyLion Malaysia",
        "location": "KL Sentral, Kuala Lumpur",
        "salary_min": 5500.0,
        "salary_max": 8500.0,
        "salary_currency": "MYR",
        "skills": ["Python", "JavaScript", "Git", "SQL"],
        "description": "Automate front-end and API testing using Python, JavaScript, and Selenium/Cypress tools. Degree or Diploma. Familiarity with SQL and Git is required. MMU or APU graduates are highly encouraged.",
        "posting_date": "2026-04-10",
        "url": "https://www.moneylion.com/careers/qa-automation",
        "qualification": "Degree",
        "university_tags": "MMU, APU"
    },
    {
        "title": "Node.js Backend Developer",
        "company": "Fave Malaysia",
        "location": "Bangsar South, Kuala Lumpur",
        "salary_min": 6000.0,
        "salary_max": 9000.0,
        "salary_currency": "MYR",
        "skills": ["Node.js", "JavaScript", "SQL", "Git"],
        "description": "Fave is a leading fintech platform. We are seeking a Node.js software developer to maintain local payment APIs. Degree or Diploma in Software Engineering. Key stack: Node.js, JavaScript, SQL databases, Git.",
        "posting_date": "2026-03-25",
        "url": "https://careers.myfave.com/node-dev",
        "qualification": "Diploma",
        "university_tags": ""
    },
    {
        "title": "Lead Software Architect",
        "company": "Petronas",
        "location": "KLCC, Kuala Lumpur",
        "salary_min": 15000.0,
        "salary_max": 25000.0,
        "salary_currency": "MYR",
        "skills": ["Java", "Python", "SQL", "Docker", "Git", "AWS"],
        "description": "Lead structural designs of cloud solutions for Malaysia's national oil and gas company. A Master or PhD in Computer Science or IT. Experience with Java, Python, SQL, Docker containers, and AWS architectures is essential.",
        "posting_date": "2026-03-15",
        "url": "https://www.petronas.com/careers/lead-architect",
        "qualification": "Master",
        "university_tags": ""
    }
]

def run():
    print("Initializing SQLite database...")
    init_db()
    
    print(f"Seeding database with {len(SEED_JOBS)} jobs...")
    inserted, updated = save_jobs(SEED_JOBS)
    print(f"Seed complete. Inserted: {inserted}, Updated: {updated}")
    
    stats = get_db_stats()
    print("\nDatabase Statistics:")
    for k, v in stats.items():
        print(f"  - {k}: {v}")

if __name__ == "__main__":
    run()
