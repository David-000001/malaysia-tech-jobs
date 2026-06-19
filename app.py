import streamlit as st
import pandas as pd
import numpy as np
import io
import sys
from datetime import datetime

# Configure page metadata
st.set_page_config(
    page_title="Malaysia Tech Job Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add parent directory to path to ensure modules are importable
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_jobs, get_db_stats, save_jobs, init_db
from scraper.hiredly_scraper import HiredlyScraper
from scraper.jobstreet_scraper import JobStreetScraper
from scraper.mock_scraper import MockScraper
from nlp.resume_processor import extract_text_from_pdf, match_resume_to_job
import analytics.visualizer as vis

# Ensure database is initialized
init_db()

# Custom UI styling injection for clean, professional dark-theme look
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* Base page background styling */
.main {
    background-color: #0b0f19;
    color: #f1f5f9;
}

/* Glassmorphism KPI Card Styling */
.kpi-card {
    background: rgba(17, 24, 39, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 15px 0 rgba(0, 0, 0, 0.2);
}

.kpi-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #0d9488; /* Teal 600 */
    line-height: 1;
}

.kpi-subtitle {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 4px;
}

/* Text highlight helper */
.highlight-teal {
    color: #2dd4bf;
    font-weight: 600;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
}

.stTabs [data-baseweb="tab"] {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 10px 18px;
    color: #94a3b8;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background-color: #0d9488 !important;
    border-color: #0d9488 !important;
    color: white !important;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3);
}

.tag {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 5px;
    margin-bottom: 5px;
}

.tag-skill {
    background-color: rgba(13, 148, 136, 0.15);
    color: #2dd4bf;
    border: 1px solid rgba(13, 148, 136, 0.3);
}

.tag-uni {
    background-color: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.3);
}

.tag-qual {
    background-color: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.3);
}
</style>
""", unsafe_allow_html=True)

# Application Header & Sidebar Configuration
st.sidebar.markdown(
    "<h2 style='text-align: center; color: #2dd4bf;'>🇲🇾 TechMarket IQ</h2>", 
    unsafe_allow_html=True
)
st.sidebar.markdown("Market intelligence and talent matcher optimized for Kuala Lumpur & Selangor technology regions.")
st.sidebar.markdown("---")

# Refresh DB Helper
def refresh_data():
    st.session_state["jobs"] = get_jobs()
    st.session_state["stats"] = get_db_stats()

if "jobs" not in st.session_state:
    refresh_data()

jobs_list = st.session_state["jobs"]
stats = st.session_state["stats"]

# Main Title
st.markdown(
    "<h1 style='margin-bottom: 0px;'>Malaysia Tech Job Market Dashboard</h1>"
    "<p style='color: #94a3b8; font-size: 1.1rem; margin-top:0px;'>Real-time scraping, analytics, and resume matching engine</p>",
    unsafe_allow_html=True
)

# Tabs
tab_insights, tab_explorer, tab_matcher, tab_scraper, tab_portfolio = st.tabs([
    "📊 Intelligence Hub", 
    "🔍 Job Explorer", 
    "📄 Resume Matcher", 
    "⚙️ Scraper Admin", 
    "💼 'Hire Me' Section"
])

# ----------------- TABS IMPLEMENTATION -----------------

# TAB 1: INTELLIGENCE HUB
with tab_insights:
    st.markdown("### Market Overview")
    
    # KPI Grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"<div class='kpi-card'>"
            f"  <div class='kpi-title'>Total Tracked Jobs</div>"
            f"  <div class='kpi-value'>{stats.get('total_jobs', 0)}</div>"
            f"  <div class='kpi-subtitle'>Active local listings</div>"
            f"</div>", 
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            f"<div class='kpi-card'>"
            f"  <div class='kpi-title'>Active Companies</div>"
            f"  <div class='kpi-value'>{stats.get('total_companies', 0)}</div>"
            f"  <div class='kpi-subtitle'>Hiring in KL & Selangor</div>"
            f"</div>", 
            unsafe_allow_html=True
        )
        
    with col3:
        avg_max_salary = stats.get("avg_max_salary", 0.0)
        st.markdown(
            f"<div class='kpi-card'>"
            f"  <div class='kpi-title'>Average Max Salary</div>"
            f"  <div class='kpi-value'>RM {avg_max_salary:,.0f}</div>"
            f"  <div class='kpi-subtitle'>Per month (where specified)</div>"
            f"</div>", 
            unsafe_allow_html=True
        )
        
    with col4:
        # Calculate most demanded skill
        all_skills = []
        for j in jobs_list:
            all_skills.extend(j.get("skills", []))
        top_skill = "Python"
        if all_skills:
            from collections import Counter
            top_skill = Counter(all_skills).most_common(1)[0][0]
            
        st.markdown(
            f"<div class='kpi-card'>"
            f"  <div class='kpi-title'>Most Demanded Skill</div>"
            f"  <div class='kpi-value'>{top_skill}</div>"
            f"  <div class='kpi-subtitle'>Appears in most listings</div>"
            f"</div>", 
            unsafe_allow_html=True
        )

    # Core Charts Grid
    st.markdown("---")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        skill_fig = vis.generate_skill_demand_chart(jobs_list)
        st.plotly_chart(skill_fig, use_container_width=True)
        
    with chart_col2:
        map_fig = vis.generate_talent_heatmap(jobs_list)
        st.plotly_chart(map_fig, use_container_width=True)

    # Trends and Leaderboard
    st.markdown("---")
    trend_col1, trend_col2 = st.columns([3, 2])
    
    with trend_col1:
        st.markdown("#### Hiring Activity Timelines")
        trend_tabs = st.tabs(["Overall Trends", "Company Trends"])
        with trend_tabs[0]:
            overall_trend_fig = vis.generate_hiring_trends_chart(jobs_list)
            st.plotly_chart(overall_trend_fig, use_container_width=True)
        with trend_tabs[1]:
            comp_trend_fig = vis.generate_company_trends_chart(jobs_list)
            st.plotly_chart(comp_trend_fig, use_container_width=True)
            
    with trend_col2:
        st.markdown("#### Hiring Activity Leaderboard")
        leaderboard_df = vis.generate_hiring_activity_table(jobs_list)
        
        # Display as styled dataframe
        st.dataframe(
            leaderboard_df,
            column_config={
                "Company": st.column_config.TextColumn("Company"),
                "Active Postings": st.column_config.ProgressColumn(
                    "Active Postings",
                    help="Total job postings in database",
                    format="%d",
                    min_value=0,
                    max_value=int(leaderboard_df["Active Postings"].max() if not leaderboard_df.empty else 10),
                ),
                "Primary Location": st.column_config.TextColumn("Main Location"),
            },
            hide_index=True,
            use_container_width=True
        )


# TAB 2: JOB EXPLORER
with tab_explorer:
    st.markdown("### Job Explorer & Search Engine")
    
    # Filter controls in sidebar or expandable container
    with st.expander("🔍 Filter Controls", expanded=True):
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            search_title = st.text_input("Job Title / Key Terms", placeholder="e.g. Python Developer")
            search_company = st.text_input("Company Name", placeholder="e.g. Grab")
        with fcol2:
            location_options = ["All", "Kuala Lumpur", "Selangor", "Bangsar South", "KL Sentral", "Cyberjaya", "Mid Valley"]
            search_location = st.selectbox("Location Focus", location_options)
            qual_options = ["All", "SPM", "STPM", "Diploma", "Degree", "Master", "PhD"]
            search_qual = st.selectbox("Minimum Qualification Required", qual_options)
        with fcol3:
            search_skill = st.text_input("Skill Requirement", placeholder="e.g. React")
            search_uni = st.text_input("Prefer University Alum", placeholder="e.g. UM")
            
        sal_min_slider = st.slider("Minimum Desired Salary (RM / month)", min_value=0, max_value=25000, value=0, step=500)

    # Execute search query
    filters = {
        "title": search_title,
        "company": search_company,
        "location": None if search_location == "All" else search_location,
        "qualification": search_qual,
        "skill": search_skill,
        "university": search_uni,
        "min_salary": sal_min_slider if sal_min_slider > 0 else None
    }
    
    filtered_jobs = get_jobs(filters)
    
    st.markdown(f"Found **{len(filtered_jobs)}** matches.")
    
    if filtered_jobs:
        # Manual pagination implementation
        jobs_per_page = 5
        total_pages = int(np.ceil(len(filtered_jobs) / jobs_per_page))
        
        # Keep track of current page in session state
        if "explorer_page" not in st.session_state:
            st.session_state["explorer_page"] = 1
            
        # Page controller widgets
        pcol1, pcol2, pcol3 = st.columns([1, 8, 1])
        with pcol1:
            if st.button("Previous", disabled=(st.session_state["explorer_page"] == 1), key="prev_btn"):
                st.session_state["explorer_page"] -= 1
        with pcol2:
            st.markdown(f"<p style='text-align: center; color: #94a3b8; margin-top: 5px;'>Page {st.session_state['explorer_page']} of {total_pages}</p>", unsafe_allow_html=True)
        with pcol3:
            if st.button("Next", disabled=(st.session_state["explorer_page"] == total_pages), key="next_btn"):
                st.session_state["explorer_page"] += 1
                
        # Slice jobs list
        start_idx = (st.session_state["explorer_page"] - 1) * jobs_per_page
        end_idx = start_idx + jobs_per_page
        page_jobs = filtered_jobs[start_idx:end_idx]
        
        # Display jobs
        for job in page_jobs:
            with st.container():
                st.markdown("---")
                jcol1, jcol2 = st.columns([3, 1])
                
                with jcol1:
                    st.markdown(f"<h4 style='margin-bottom:2px;'>{job['title']}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size: 0.95rem; color:#2dd4bf; margin-bottom:5px;'>{job['company']} — {job['location']}</p>", unsafe_allow_html=True)
                    
                    # Tags list
                    tags_html = ""
                    # Qualification tag
                    if job.get("qualification") and job.get("qualification") != "Not Specified":
                        tags_html += f"<span class='tag tag-qual'>{job['qualification']}</span>"
                    # University tags
                    for u in job.get("university_tags", []):
                        tags_html += f"<span class='tag tag-uni'>{u} Alum Preferred</span>"
                    # Skills tags
                    for s in job.get("skills", []):
                        tags_html += f"<span class='tag tag-skill'>{s}</span>"
                        
                    if tags_html:
                        st.markdown(tags_html, unsafe_allow_html=True)
                        
                    st.write(job["description"])
                    
                with jcol2:
                    st.markdown("<p style='text-align: right; margin-top: 10px;'>Salary Estimate</p>", unsafe_allow_html=True)
                    if job.get("salary_min") and job.get("salary_max"):
                        st.markdown(f"<h4 style='text-align: right; color:#2dd4bf; margin-top:-10px;'>RM {job['salary_min']:,.0f} - {job['salary_max']:,.0f}</h4>", unsafe_allow_html=True)
                    elif job.get("salary_min"):
                        st.markdown(f"<h4 style='text-align: right; color:#2dd4bf; margin-top:-10px;'>RM {job['salary_min']:,.0f}+</h4>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p style='text-align: right; color:#64748b; font-style:italic; margin-top:-10px;'>Not Specified</p>", unsafe_allow_html=True)
                        
                    # Matching Shortcut
                    st.markdown(f"<p style='text-align: right; color: #64748b; font-size: 0.8rem;'>Posted: {job['posting_date']}</p>", unsafe_allow_html=True)
                    
                    # Apply action
                    st.markdown(f"<div style='text-align: right;'><a href='{job['url']}' target='_blank'><button style='background-color:#1e293b; color:#2dd4bf; border: 1px solid #0d9488; padding:6px 12px; border-radius:6px; cursor:pointer;'>Apply on Live Site</button></a></div>", unsafe_allow_html=True)
    else:
        st.info("No job postings found matching the search criteria. Try modifying your filters.")


# TAB 3: RESUME MATCHER
with tab_matcher:
    st.markdown("### Smart Resume Matching System (NLP)")
    st.markdown("Upload your PDF resume to analyze your tech skill set, detect qualifications, and compute matching scores against local job opportunities.")
    
    # Multi-column: 1. Upload & Resume Analysis 2. Match Target & Results
    m_col1, m_col2 = st.columns([1, 1])
    
    # Sample resume generator
    sample_resume_text = """
    Ahmad Danish
    Kuala Lumpur, Malaysia | danish.dev@email.com
    
    Education:
    Bachelor of Computer Science (Honours) - Universiti Malaya (UM)
    Highest Qualification: Degree
    Languages: English (Fluent), Malay (Native), Mandarin (Conversational)
    
    Technical Skills:
    Programming: Python, JavaScript, PHP
    Web Frameworks: React, Laravel, Node.js
    Database & Cloud: SQL (MySQL, PostgreSQL), AWS (S3, EC2)
    Tools: Git, Docker, GitHub
    
    Experience:
    Software Engineering Intern at Grab Malaysia
    - Developed API integrations using Python and Laravel.
    - Containerized development environments using Docker.
    - Utilized Git for version control and collaborated with backend teams.
    """
    
    with m_col1:
        st.markdown("#### 1. Upload CV / Resume")
        
        # Download Sample Resume Button
        st.download_button(
            label="📄 Download Sample CV (for testing)",
            data=sample_resume_text,
            file_name="ahmad_danish_sample_cv.txt",
            mime="text/plain",
            help="Download a pre-made text resume detailing skills like Python, React, Laravel, AWS, and Docker to test the matching engine."
        )
        
        uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
        
        resume_text = ""
        if uploaded_file is not None:
            with st.spinner("Extracting text and identifying credentials from PDF..."):
                pdf_bytes = uploaded_file.read()
                resume_text = extract_text_from_pdf(pdf_bytes)
                
            if not resume_text:
                st.error("Failed to extract text from this PDF. Please verify that it is not scanned/image-only or corrupted.")
        else:
            st.info("Or paste your raw resume text below to execute analysis:")
            resume_text = st.text_area("Paste Resume Text Here", height=200, value="")
            
        if resume_text:
            st.success("Resume data successfully loaded!")
            
            # Analyze resume credentials
            from nlp.resume_processor import extract_skills, extract_qualification, extract_languages
            extracted_sk = extract_skills(resume_text)
            extracted_ql = extract_qualification(resume_text)
            extracted_ln = extract_languages(resume_text)
            
            with st.container():
                st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
                st.markdown("<h5 style='margin-top:0px;'>Extracted Credentials</h5>", unsafe_allow_html=True)
                
                st.write(f"🎓 **Detected Qualification**: {extracted_ql}")
                
                st.write("🗣️ **Languages Detected**:")
                langs_html = ""
                for l in extracted_ln:
                    langs_html += f"<span class='tag tag-uni'>{l}</span>"
                if langs_html:
                    st.markdown(langs_html, unsafe_allow_html=True)
                else:
                    st.write("*None explicitly detected*")
                    
                st.write("🛠️ **Skills Identified**:")
                skills_html = ""
                for s in extracted_sk:
                    skills_html += f"<span class='tag tag-skill'>{s}</span>"
                if skills_html:
                    st.markdown(skills_html, unsafe_allow_html=True)
                else:
                    st.write("*No matched technical skills from the Malaysian core list found.*")
                    
                st.markdown("</div>", unsafe_allow_html=True)
                
    with m_col2:
        st.markdown("#### 2. Select Job Opportunity to Match")
        
        if not jobs_list:
            st.warning("Database contains no jobs to match against. Please run the scraper or seed data first.")
        else:
            # Dropdown options
            job_options = [f"{j['title']} at {j['company']} ({j['location']})" for j in jobs_list]
            selected_option = st.selectbox("Select Target Job", job_options)
            
            # Retrieve selected job dict
            selected_idx = job_options.index(selected_option)
            selected_job = jobs_list[selected_idx]
            
            if resume_text:
                # Compute Match
                match_results = match_resume_to_job(resume_text, selected_job)
                
                # Match Percentage Gauge Display
                score = match_results["match_percentage"]
                
                st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
                st.markdown("<h5 style='margin-top:0px;'>Match Report</h5>", unsafe_allow_html=True)
                
                # Dynamic color selection for score
                score_color = "#ef4444" # Red
                if score >= 70.0:
                    score_color = "#10b981" # Green
                elif score >= 40.0:
                    score_color = "#f59e0b" # Orange
                    
                st.markdown(
                    f"<div style='text-align:center; padding: 10px;'>"
                    f"  <h1 style='color:{score_color}; font-size:4rem; margin-bottom: 0px;'>{score}%</h1>"
                    f"  <p style='color:#94a3b8; margin-top:0px;'>Skill Compatibility Index</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                
                # Matched and missing details
                st.write("✅ **Matched Skills**:")
                m_html = ""
                for s in match_results["matched_skills"]:
                    m_html += f"<span class='tag tag-skill' style='border-color:#10b981; color:#34d399;'>{s}</span>"
                st.markdown(m_html if m_html else "*None*", unsafe_allow_html=True)
                
                st.write("❌ **Missing Required Skills**:")
                ms_html = ""
                for s in match_results["missing_skills"]:
                    ms_html += f"<span class='tag tag-skill' style='border-color:#ef4444; color:#f87171;'>{s}</span>"
                st.markdown(ms_html if ms_html else "*None! Perfect compatibility.*", unsafe_allow_html=True)
                
                # Education verification
                job_qual = selected_job.get("qualification", "Not Specified")
                cand_qual = match_results["qualification"]
                
                # Check mapping ranks
                qual_rank = {"Not Specified": 0, "SPM": 1, "STPM": 2, "Diploma": 3, "Degree": 4, "Master": 5, "PhD": 6}
                cand_rank_val = qual_rank.get(cand_qual, 0)
                job_rank_val = qual_rank.get(job_qual, 0)
                
                st.write("🎓 **Education Alignment Check**:")
                if cand_rank_val >= job_rank_val:
                    st.write(f"✔️ Qualified! (Required: `{job_qual}` | Candidates: `{cand_qual}`)")
                else:
                    st.write(f"⚠️ Education gap (Required: `{job_qual}` | Candidates: `{cand_qual}`)")
                    
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Course recommendations for missing elements
                if match_results["recommendations"]:
                    st.markdown("#### 📚 Recommended Up-skilling Paths")
                    for rec in match_results["recommendations"]:
                        st.markdown(f"**Missing: `{rec['skill']}`**")
                        for res in rec["resources"]:
                            st.markdown(f"- [{res['name']}]({res['url']})")
                else:
                    st.balloons()
                    st.success("Awesome! You possess 100% of the required tech skills for this role.")
            else:
                st.info("Please upload a resume or paste text on the left to see the match report.")


# TAB 4: SCRAPER ADMIN CONSOLE
with tab_scraper:
    st.markdown("### Job Harvester Console")
    st.markdown("Control panel to scrape job sites live or run a high-fidelity local simulator for demonstration purposes.")
    
    sc_col1, sc_col2 = st.columns([1, 2])
    
    with sc_col1:
        st.markdown("#### Scraper Setup")
        
        # Sim switch
        simulate = st.checkbox("Simulate Live Scraping (Recommended)", value=True, 
                               help="Simulates scraping activity and network delays without hitting live rate limits or Cloudflare blockers. Perfect for recruiter evaluations.")
        
        # Scrape target selection
        sources = st.multiselect("Scraping Targets", ["JobStreet Malaysia", "Hiredly"], default=["JobStreet Malaysia", "Hiredly"])
        
        # Query search term
        scrape_query = st.text_input("Keywords / Tech Query", value="Developer", help="e.g. React, Python, Data Scientist")
        
        # Limit pages
        scrape_pages = st.slider("Maximum Pages to Fetch", min_value=1, max_value=5, value=2)
        
        # Delay
        scrape_delay = st.slider("Polite request delays (Seconds)", min_value=1.0, max_value=5.0, value=2.0)
        
        run_scraper = st.button("🚀 Trigger Scraper Run")
        
    with sc_col2:
        st.markdown("#### Real-time Harvest Log Output")
        
        if run_scraper:
            if not sources:
                st.warning("Please choose at least one scraper source (JobStreet or Hiredly).")
            else:
                # Capture print logs to display in code box
                log_capture = io.StringIO()
                sys.stdout = log_capture
                
                # Progress Bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total_scraped = []
                
                try:
                    # Execute mock or real scraping
                    if simulate:
                        status_text.text("Connecting simulator to live streams...")
                        progress_bar.progress(10)
                        
                        mock_scr = MockScraper(delay=scrape_delay)
                        
                        # Split by sources to show logical separation
                        for idx, source in enumerate(sources):
                            status_text.text(f"Scraping simulated data stream for {source}...")
                            progress_bar.progress(30 + (idx * 30))
                            results = mock_scr.scrape_jobs(query=scrape_query, max_pages=scrape_pages)
                            total_scraped.extend(results)
                            
                        progress_bar.progress(90)
                    else:
                        status_text.text("Initiating live scrapers (establishing sessions)...")
                        progress_bar.progress(10)
                        
                        for idx, source in enumerate(sources):
                            if source == "Hiredly":
                                status_text.text("Connecting to Hiredly.com...")
                                progress_bar.progress(20 + (idx * 30))
                                scraper = HiredlyScraper(delay=scrape_delay)
                                results = scraper.scrape_jobs(query=scrape_query, max_pages=scrape_pages)
                                total_scraped.extend(results)
                            elif source == "JobStreet Malaysia":
                                status_text.text("Connecting to JobStreet.com.my...")
                                progress_bar.progress(20 + (idx * 30))
                                scraper = JobStreetScraper(delay=scrape_delay)
                                results = scraper.scrape_jobs(query=scrape_query, max_pages=scrape_pages)
                                total_scraped.extend(results)
                                
                        progress_bar.progress(90)
                        
                    status_text.text("Storing scraped listings into SQLite database...")
                    # Save results to db
                    if total_scraped:
                        inserted, updated = save_jobs(total_scraped)
                        print(f"\n[Database] Operation completed. Inserted: {inserted} | Updated: {updated}")
                    else:
                        print("\n[Database] No records extracted during this run.")
                        
                except Exception as run_err:
                    print(f"\n[Error] Scraper execution failed: {run_err}")
                finally:
                    # Restore stdout
                    sys.stdout = sys.__stdout__
                    
                progress_bar.progress(100)
                status_text.text("Scrape complete!")
                
                # Fetch output logs
                logs = log_capture.getvalue()
                
                # Render inside styled console box
                st.code(logs if logs else "No logs produced.", language="text")
                
                # Update Session State Data
                refresh_data()
                st.success(f"Harvest finished successfully! Harvester collected {len(total_scraped)} jobs.")
        else:
            st.info("Press 'Trigger Scraper Run' to execute crawling and watch console logs populate.")


# TAB 5: PORTFOLIO / HIRE ME
with tab_portfolio:
    st.markdown("### 💼 Candidate Portfolio ('Hire Me')")

    pcol1, pcol2 = st.columns([1, 2])
    with pcol1:
        st.markdown(
            """
            <div style='background: linear-gradient(135deg, #0d9488, #0f172a); border-radius: 16px; padding: 28px; text-align: center; border: 1px solid rgba(13,148,136,0.3);'>
                <h2 style='color: #2dd4bf; margin-bottom: 4px; font-size: 1.6rem;'>AVIJIT CHANDRA DEY</h2>
                <p style='color: #94a3b8; font-size: 0.9rem; margin-bottom: 16px;'>AI Engineer</p>
                <hr style='border-color: rgba(255,255,255,0.1); margin: 12px 0;'>
                <p style='color: #cbd5e1; font-size: 0.85rem; line-height: 1.6;'>
                    Specialising in Machine Learning, Deep Learning, Computer Vision, and AI solutions.
                </p>
                <div style='margin-top: 16px;'>
                    <span class='tag tag-skill'>ML</span>
                    <span class='tag tag-skill'>DL</span>
                    <span class='tag tag-skill'>CVPR</span>
                    <span class='tag tag-skill'>AI</span>
                    <span class='tag tag-skill'>Python</span>
                    <span class='tag tag-skill'>SQL</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔗 Connect on LinkedIn", use_container_width=True):
            st.markdown("[Open LinkedIn](https://www.linkedin.com/in/avijit-chandra-dey-340b61294/)", unsafe_allow_html=True)
        st.markdown(
            "<a href='https://www.linkedin.com/in/avijit-chandra-dey-340b61294/' target='_blank' style='display:block; text-align:center; margin-top:-8px; color:#64748b; font-size:0.75rem;'>https://linkedin.com/in/avijit-chandra-dey-340b61294</a>",
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🐝 GitHub Profile", use_container_width=True):
            st.markdown("[Open GitHub](https://github.com/David-000001)", unsafe_allow_html=True)
        st.markdown(
            "<a href='https://github.com/David-000001' target='_blank' style='display:block; text-align:center; margin-top:-8px; color:#64748b; font-size:0.75rem;'>github.com/David-000001</a>",
            unsafe_allow_html=True
        )

    with pcol2:
        st.markdown("#### Technical Capabilities & Focus")
        st.write("""
B.CS (AI) Student at Universiti Malaya | Building Practical Projects in Python, SQL, Java, and Data Analysis | Open to Internship Roles in KL.
        """)

        st.markdown("##### Key Strengths:")
        st.markdown("""
- **Brainstormer:** Approaches problems creatively, generating innovative solutions and ideas across technical and analytical challenges.
- **Hard Worker:** Committed to delivering high-quality results, consistently going the extra mile on every project.
- **Fast Learner:** Quickly picks up new technologies, frameworks, and concepts — from ML pipelines to full-stack deployments.
        """)

        # CV Download
        st.markdown("---")
        st.markdown("##### 📄 Curriculum Vitae")
        st.markdown(
            """
            <a href='https://drive.google.com/file/d/1f6sYe56u0_sQcRYkvAjXUVnvqjIfFBZl/view?usp=sharing' target='_blank'>
                <button style='background:#0d9488; color:white; border:none; padding:10px 20px; border-radius:8px; cursor:pointer; font-size:0.9rem; width:100%;'>
                    📂 Download / View 1-Page CV
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; color:#64748b; font-size:0.8rem;'>Malaysia Tech Job Market Dashboard &copy; 2026 | Built for Malaysia Tech Talent Evaluation</p>",
        unsafe_allow_html=True
    )
