import time
import random
import re
import requests

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 OPR/99.0.0.0"
]

class BaseScraper:
    def __init__(self, delay=2.0):
        self.delay = delay
        self.session = requests.Session()
        
    def get_headers(self):
        """Returns rotating headers to bypass simple user-agent blocking."""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
    def wait_polite(self):
        """Delays request execution to respect server capacity."""
        sleep_time = self.delay + random.uniform(0.5, 2.0)
        time.sleep(sleep_time)
        
    def fetch_page(self, url, params=None):
        """Politely fetches content from a URL."""
        self.wait_polite()
        headers = self.get_headers()
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to fetch {url}: Status code {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def clean_location(self, loc_text):
        """Maps location keywords to normalized regions (Kuala Lumpur or Selangor) and hubs."""
        if not loc_text:
            return "Kuala Lumpur"
        
        loc_lower = loc_text.lower()
        
        # Check specific hubs
        if "bangsar south" in loc_lower:
            return "Bangsar South, Kuala Lumpur"
        elif "kl sentral" in loc_lower or "kuala lumpur sentral" in loc_lower:
            return "KL Sentral, Kuala Lumpur"
        elif "cyberjaya" in loc_lower:
            return "Cyberjaya, Selangor"
        elif "mid valley" in loc_lower or "midvalley" in loc_lower:
            return "Mid Valley, Kuala Lumpur"
        elif "petaling jaya" in loc_lower or "mutiara damansara" in loc_lower or "damansara" in loc_lower or "pj" in loc_lower:
            return "Petaling Jaya, Selangor"
        elif "shah alam" in loc_lower:
            return "Shah Alam, Selangor"
        elif "subang" in loc_lower:
            return "Subang Jaya, Selangor"
        elif "puchong" in loc_lower:
            return "Puchong, Selangor"
            
        # Fallbacks
        if "selangor" in loc_lower:
            return "Selangor"
        if "kuala lumpur" in loc_lower or "kl" in loc_lower:
            return "Kuala Lumpur"
            
        return loc_text.strip()

    def parse_qualification(self, text):
        """Extracts required qualifications from job descriptions."""
        if not text:
            return "Not Specified"
        text_lower = text.lower()
        if "phd" in text_lower or "ph.d" in text_lower or "doctorate" in text_lower:
            return "PhD"
        elif "master" in text_lower or "postgraduate" in text_lower:
            return "Master"
        elif "degree" in text_lower or "bachelor" in text_lower or "undergraduate" in text_lower or "graduate" in text_lower:
            return "Degree"
        elif "diploma" in text_lower:
            return "Diploma"
        elif "stpm" in text_lower or "a-level" in text_lower or "matriculation" in text_lower:
            return "STPM"
        elif "spm" in text_lower or "o-level" in text_lower or "high school" in text_lower:
            return "SPM"
        return "Not Specified"

    def parse_universities(self, text):
        """Identifies mentions of local Malaysian universities."""
        if not text:
            return []
        text_lower = text.lower()
        unis = []
        mapping = {
            "UM": ["universiti malaya", "university of malaya", r"\bum\b"],
            "USM": ["universiti sains malaysia", "university of science malaysia", r"\busm\b"],
            "UKM": ["universiti kebangsaan malaysia", "national university of malaysia", r"\bukm\b"],
            "UPM": ["universiti putra malaysia", r"\bupm\b"],
            "UTM": ["universiti teknologi malaysia", r"\butm\b"],
            "UiTM": ["universiti teknologi mara", r"\buitm\b"],
            "Monash": ["monash university", "monash malaysia", r"\bmonash\b"],
            "Taylor's": ["taylor's university", "taylors university", "taylor's", "taylors"],
            "Sunway": ["sunway university", "sunway college", r"\bsunway\b"],
            "MMU": ["multimedia university", r"\bmmu\b"],
            "APU": ["asia pacific university", r"\bapu\b"],
            "UTAR": ["universiti tunku abdul rahman", r"\butar\b"]
        }
        for uni, patterns in mapping.items():
            for pattern in patterns:
                if "\\" in pattern:
                    if re.search(pattern, text_lower):
                        unis.append(uni)
                        break
                else:
                    if pattern in text_lower:
                        unis.append(uni)
                        break
        return list(set(unis))

    def extract_skills(self, text):
        """Matches text against a curated list of Malaysian tech skills."""
        if not text:
            return []
        text_lower = text.lower()
        curated_skills = {
            "Python": ["python"],
            "Java": [r"\bjava\b"],
            "JavaScript": ["javascript", "js", "ecmascript"],
            "React": ["react", "react.js", "reactjs", "react native"],
            "Node.js": ["node.js", "nodejs", "node"],
            "Laravel": ["laravel"],
            "PHP": ["php"],
            "AWS": ["aws", "amazon web services"],
            "SQL": ["sql", "mysql", "postgresql", "sqlite", "oracle", "sql server"],
            "Docker": ["docker", "container"],
            "Git": ["git", "github", "gitlab"],
            "SAP": ["sap"],
            "Kotlin": ["kotlin"],
            "Swift": ["swift"],
            "Flutter": ["flutter"],
            "Go": ["go lang", r"\bgolang\b", r"\bgo\b"]
        }
        matched = []
        for skill, patterns in curated_skills.items():
            for pattern in patterns:
                if "\\" in pattern or len(pattern) <= 3:
                    p = pattern if "\\" in pattern else rf"\b{pattern}\b"
                    if re.search(p, text_lower):
                        matched.append(skill)
                        break
                else:
                    if pattern in text_lower:
                        matched.append(skill)
                        break
        return matched
