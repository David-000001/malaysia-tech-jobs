# 📺 TechMarket IQ: 2-Minute Demo Presentation Script

This script is structured to guide a 2-minute presentation or screen recording demonstrating the core functionalities of the **Malaysia Tech Job Market Intelligence Dashboard** to recruiters, HR professionals, or technical assessors.

---

## ⏱️ Timeline & Script Outline

### Phase 1: Introduction & Intelligence Hub (0:00 - 0:35)
* **Visuals**: Display the **📊 Intelligence Hub** tab.
* **Speaker Script**:
  > *"Hello! Today, I’m presenting **TechMarket IQ**, a live job market analytics and NLP recruitment solution optimized for Kuala Lumpur and Selangor. 
  > Here in the Intelligence Hub, we instantly see a high-level overview of local tech trends: we are tracking active tech roles, average salaries, and the most demanded skill sets. 
  > On the left, our horizontal bar chart ranks the top 10 most in-demand skills dynamically compiled from jobs. On the right, our open-street geocoding map overlays these postings to show talent hotspots. We can clearly see a high concentration of jobs in Bangsar South, Cyberjaya, and KL Sentral. Further down, our trend lines track monthly posting volumes per company, showing who is scaling up."*

### Phase 2: Live Job Harvesting (0:35 - 1:05)
* **Visuals**: Click on the **⚙️ Scraper Admin** tab. Leave the "Simulate Live Scraping" checkbox checked. Click the **🚀 Trigger Scraper Run** button.
* **Speaker Script**:
  > *"Let's see how we gather this data. I will switch to the Scraper Admin console. The engine includes custom crawler agents that parse platforms like JobStreet Malaysia and Hiredly. To safeguard against rate-limits, it uses random delays and rotating user-agents. 
  > I'll trigger a harvest run using our simulation mode. As the progress bar updates, a live terminal console prints our crawler logs, showing real-time agent rotations and robots.txt delay pauses. Our SQLite database is updated immediately, indicating exactly how many new records were inserted or existing jobs updated."*

### Phase 3: Job Explorer & Filtering (1:05 - 1:30)
* **Visuals**: Click on the **🔍 Job Explorer** tab. Search for *"Python"*, select *"Bangsar South"* in Location, and adjust the Min Salary slider.
* **Speaker Script**:
  > *"Now that the database is populated, we can explore jobs in the Job Explorer. Recruiters and applicants can search by keywords or company, and filter by minimum academic qualifications, university preferences, or salary brackets. The cards list standardized metadata tags, separating candidate skills, preferred universities, and educational requirements. We also have pagination for a clean, non-cluttered browsing experience."*

### Phase 4: NLP Resume Matching & Upskilling (1:30 - 1:50)
* **Visuals**: Click on the **📄 Resume Matcher** tab. Click *"Download Sample CV"*, copy or upload it, select the first job, and click run.
* **Speaker Script**:
  > *"Next, let's explore our smart matching engine. I'll download our pre-seeded student CV containing skills like Python, React, and Laravel, and load it into the parser. 
  > The engine uses spaCy NLP tokenization to identify candidate skills, qualifications, and languages. When matched against our Grab Python Developer job, we immediately get a matching score. It checks for educational alignment, flags missing skills like Docker, and dynamically builds learning links to YouTube and freeCodeCamp courses to guide candidates to close their skills gap."*

### Phase 5: "Hire Me" & Conclusion (1:50 - 2:00)
* **Visuals**: Click on the **💼 'Hire Me' Section** tab.
* **Speaker Script**:
  > *"Finally, we have the 'Hire Me' portfolio page, introducing Ahmad Danish, a final-year CS student from Universiti Malaya. It presents his core capabilities, internship experience at Grab, and provides a direct one-click download for his 1-page professional CV alongside LinkedIn links. 
  > This dashboard bridges the gap between raw web scraping, data analytics, and NLP matching. Thank you for your time!"*
