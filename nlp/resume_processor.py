import io
import re
import PyPDF2

# Attempt to load spacy
nlp = None
try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # Try to download if not present
        import spacy.cli
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
except Exception as e:
    print(f"Warning: Could not load or download spaCy. Falling back to regex parser. Detail: {e}")

# Skill directories (Malaysian focused)
CURATED_SKILLS = {
    "Python": ["python", "pandas", "numpy", "django", "flask", "fastapi"],
    "Java": [r"\bjava\b", "springboot", "spring boot"],
    "JavaScript": ["javascript", "js", "ecmascript", "typescript", "ts"],
    "React": ["react", "react.js", "reactjs", "react native", "next.js", "nextjs"],
    "Node.js": ["node.js", "nodejs", "node", "express"],
    "Laravel": ["laravel"],
    "PHP": ["php"],
    "AWS": ["aws", "amazon web services", "s3", "ec2", "rds", "lambda"],
    "SQL": ["sql", "mysql", "postgresql", "sqlite", "oracle", "sql server", "nosql", "mongodb"],
    "Docker": ["docker", "kubernetes", "k8s", "container"],
    "Git": ["git", "github", "gitlab", "bitbucket"],
    "SAP": ["sap", "abap", "sap hana"],
    "Kotlin": ["kotlin"],
    "Swift": ["swift", "swiftui"],
    "Flutter": ["flutter", "dart"],
    "Go": ["go lang", "golang", r"\bgo\b"]
}

# Curated Learning Resources for missing skills
LEARNING_RESOURCES = {
    "Python": [
        {"name": "Python for Beginners (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw"},
        {"name": "Official Python Documentation", "url": "https://docs.python.org/"}
    ],
    "Java": [
        {"name": "Java Tutorial for Beginners (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=grEKMHGYyns"},
        {"name": "Java Documentation", "url": "https://docs.oracle.com/en/java/"}
    ],
    "JavaScript": [
        {"name": "JavaScript Tutorial for Beginners (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=PkZNo7F5NJk"},
        {"name": "MDN JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript"}
    ],
    "React": [
        {"name": "React JS Full Course (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=bMknfKXIFA8"},
        {"name": "Official React Documentation", "url": "https://react.dev/"}
    ],
    "Node.js": [
        {"name": "Node.js and Express Course (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=Oe421EPjeBE"},
        {"name": "Node.js Documentation", "url": "https://nodejs.org/en/docs/"}
    ],
    "Laravel": [
        {"name": "Laravel for Beginners (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=ImtZ5yENzgE"},
        {"name": "Official Laravel Documentation", "url": "https://laravel.com/docs"}
    ],
    "PHP": [
        {"name": "PHP Course for Beginners (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=OK_JCtrrv-c"},
        {"name": "Official PHP Manual", "url": "https://www.php.net/docs.php"}
    ],
    "AWS": [
        {"name": "AWS Cloud Practitioner Essentials (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=SOTamWGuqnM"},
        {"name": "Official AWS Documentation", "url": "https://docs.aws.amazon.com/"}
    ],
    "SQL": [
        {"name": "SQL Tutorial Full Database Course (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY"},
        {"name": "W3Schools SQL Tutorial", "url": "https://www.w3schools.com/sql/"}
    ],
    "Docker": [
        {"name": "Docker Tutorial for Beginners (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=fqMOX6JJhGo"},
        {"name": "Official Docker Documentation", "url": "https://docs.docker.com/"}
    ],
    "Git": [
        {"name": "Git and GitHub Crash Course (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=apGV9Ad7XYY"},
        {"name": "Pro Git Book", "url": "https://git-scm.com/book/en/v2"}
    ],
    "SAP": [
        {"name": "Introduction to SAP (YouTube)", "url": "https://www.youtube.com/watch?v=j4_P3XG5Xm8"},
        {"name": "SAP Help Portal", "url": "https://help.sap.com/"}
    ],
    "Kotlin": [
        {"name": "Kotlin Course for Beginners (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=F9UC9DY-vIU"},
        {"name": "Kotlin Documentation", "url": "https://kotlinlang.org/docs/home.html"}
    ],
    "Swift": [
        {"name": "Swift Programming Tutorial (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=comS7cO5rc4"},
        {"name": "Swift.org Documentation", "url": "https://www.swift.org/documentation/"}
    ],
    "Flutter": [
        {"name": "Flutter Course for Beginners (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=VPvVD8t02U8"},
        {"name": "Official Flutter Documentation", "url": "https://docs.flutter.dev/"}
    ],
    "Go": [
        {"name": "Go Programming Tutorial (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=YS4e4q9oBaU"},
        {"name": "Official Go Documentation", "url": "https://go.dev/doc/"}
    ]
}

def extract_text_from_pdf(pdf_file_bytes):
    """Extracts all text from an uploaded PDF file bytes using PyPDF2."""
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file_bytes))
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        text = ""
    return text

def extract_skills(text):
    """
    Extracts tech skills from text. Uses spaCy tokenization if available, 
    falling back to regular expression searches.
    """
    if not text:
        return []
        
    text_lower = text.lower()
    matched = set()
    
    # NLP-enhanced extraction if spaCy is loaded
    if nlp:
        doc = nlp(text_lower)
        tokens = [token.text for token in doc]
        # Match tokens against keys and pattern terms
        for skill, patterns in CURATED_SKILLS.items():
            for pattern in patterns:
                if "\\" in pattern or len(pattern) <= 3:
                    p = pattern if "\\" in pattern else rf"\b{pattern}\b"
                    if re.search(p, text_lower):
                        matched.add(skill)
                        break
                else:
                    if pattern in tokens or pattern in text_lower:
                        matched.add(skill)
                        break
    else:
        # Regex-only fallback
        for skill, patterns in CURATED_SKILLS.items():
            for pattern in patterns:
                if "\\" in pattern or len(pattern) <= 3:
                    p = pattern if "\\" in pattern else rf"\b{pattern}\b"
                    if re.search(p, text_lower):
                        matched.add(skill)
                        break
                else:
                    if pattern in text_lower:
                        matched.add(skill)
                        break
                        
    return list(matched)

def extract_languages(text):
    """Detects languages listed on the resume."""
    if not text:
        return []
        
    text_lower = text.lower()
    languages = []
    
    mapping = {
        "English": ["english", "ielts", "toefl"],
        "Mandarin": ["mandarin", "chinese", "hsk", "cantonese"],
        "Malay": ["malay", "bahasa melayu", "bahasa malaysia", "\\bbm\\b"]
    }
    
    for lang, patterns in mapping.items():
        for pattern in patterns:
            if "\\" in pattern:
                if re.search(pattern, text_lower):
                    languages.append(lang)
                    break
            else:
                if pattern in text_lower:
                    languages.append(lang)
                    break
                    
    return languages

def extract_qualification(text):
    """Detects the candidate's highest academic qualification level."""
    if not text:
        return "Not Specified"
        
    text_lower = text.lower()
    if "phd" in text_lower or "ph.d" in text_lower or "doctor of philosophy" in text_lower:
        return "PhD"
    elif "master" in text_lower or "postgraduate" in text_lower or "m.s" in text_lower or "m.sc" in text_lower or "mba" in text_lower:
        return "Master"
    elif "degree" in text_lower or "bachelor" in text_lower or "b.s" in text_lower or "b.sc" in text_lower or "graduate" in text_lower:
        return "Degree"
    elif "diploma" in text_lower:
        return "Diploma"
    elif "stpm" in text_lower or "a-level" in text_lower or "matriculation" in text_lower or "foundation" in text_lower:
        return "STPM"
    elif "spm" in text_lower or "o-level" in text_lower or "high school" in text_lower:
        return "SPM"
        
    return "Not Specified"

def match_resume_to_job(resume_text, job):
    """
    Computes matching statistics between resume text and a job dictionary.
    
    Returns a dictionary with:
    - match_percentage: float (0 to 100)
    - matched_skills: list
    - missing_skills: list
    - resume_skills: list
    - qualification: string
    - languages: list
    - recommendations: list of resources for missing skills
    """
    resume_skills = extract_skills(resume_text)
    candidate_qual = extract_qualification(resume_text)
    candidate_langs = extract_languages(resume_text)
    
    job_skills = job.get("skills", [])
    if isinstance(job_skills, str):
         job_skills = [s.strip() for s in job_skills.split(",") if s.strip()]
         
    # Calculate match
    matched_skills = [s for s in job_skills if s in resume_skills]
    missing_skills = [s for s in job_skills if s not in resume_skills]
    
    if len(job_skills) > 0:
        match_score = len(matched_skills) / len(job_skills)
        match_percentage = round(match_score * 100, 1)
    else:
        # If the job posting lists no specific skills, we look for any matches with the resume skills in description
        job_desc = job.get("description", "")
        extracted_job_skills = extract_skills(job_desc)
        if len(extracted_job_skills) > 0:
            matched_skills = [s for s in extracted_job_skills if s in resume_skills]
            missing_skills = [s for s in extracted_job_skills if s not in resume_skills]
            match_percentage = round((len(matched_skills) / len(extracted_job_skills)) * 100, 1)
        else:
            match_percentage = 100.0 # Default fallback if no skills specified anywhere
            
    # Build recommendations
    recommendations = []
    for skill in missing_skills:
        if skill in LEARNING_RESOURCES:
            recommendations.append({
                "skill": skill,
                "resources": LEARNING_RESOURCES[skill]
            })
            
    return {
        "match_percentage": match_percentage,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "resume_skills": resume_skills,
        "qualification": candidate_qual,
        "languages": candidate_langs,
        "recommendations": recommendations
    }
