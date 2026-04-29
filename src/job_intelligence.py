import random
from urllib.parse import quote

# Company → domain mapping for logo fetching
COMPANY_DOMAINS = {
    "Google": "google.com",
    "Amazon": "amazon.com",
    "Microsoft": "microsoft.com",
    "Oracle": "oracle.com",
    "Meta": "meta.com",
    "TCS": "tcs.com",
    "Infosys": "infosys.com",
    "Wipro": "wipro.com",
    "Adobe": "adobe.com",
    "Salesforce": "salesforce.com",
    "Atlassian": "atlassian.com",
    "Uber": "uber.com",
    "Zomato": "zomato.com",
    "PhonePe": "phonepe.com",
    "Apple": "apple.com",
    "Netflix": "netflix.com",
    "Spotify": "spotify.com",
    "Deloitte": "deloitte.com",
    "Accenture": "accenture.com",
    "Razorpay": "razorpay.com",
}

import requests
import base64
import streamlit as st

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_company_logo_b64(company_name: str) -> str:
    """Server-side fetch to absorb 404s silently and return guaranteed Base64 images."""
    domain = COMPANY_DOMAINS.get(company_name, f"{company_name.lower().replace(' ', '')}.com")
    url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
    
    try:
        r = requests.get(url, timeout=2)
        if r.status_code == 200 and len(r.content) > 100:
            b64 = base64.b64encode(r.content).decode('utf-8')
            return f"data:image/png;base64,{b64}"
    except Exception:
        pass
        
    return get_company_logo_fallback(company_name)

def get_company_logo_fallback(company_name: str) -> str:
    """Generate a clean initial-based fallback logo URL."""
    initials = "".join([w[0] for w in company_name.split()[:2]]).upper()
    return f"https://ui-avatars.com/api/?name={initials}&background=0D9488&color=fff&size=64&font-size=0.4&format=svg"

def get_company_logo_fallback_api(company_name: str) -> str:
    return fetch_company_logo_b64(company_name)

def fetch_live_jobs(skills):
    """
    Simulates fetching real-time job openings from top platforms.
    In a production app, this would be an API call to a job aggregator.
    """
    roles = suggest_roles(skills)
    main_role = roles[0] if roles else "Software Engineer"
    
    companies = [
        "Google", "Amazon", "Microsoft", "Oracle", "Meta", "TCS", "Infosys", "Wipro", 
        "Adobe", "Salesforce", "Atlassian", "Uber", "Zomato", "PhonePe", "Razorpay"
    ]
    locations = ["Remote", "Bangalore, India", "Hyderabad, India", "San Francisco, CA", "Seattle, WA", "Pune, India"]
    salaries = ["$120k - $160k", "₹18L - ₹32L", "₹25L - ₹45L", "$150k - $210k", "Competitive"]
    
    jobs = []
    for i in range(8):
        co = random.choice(companies)
        loc = random.choice(locations)
        sal = random.choice(salaries)
        prefix = random.choice(["Senior", "Staff", "Lead", "Associate", "Cloud", "Neural"])
        title = f"{prefix} {main_role}"
        
        encoded_query = quote(title)
        query_dash = title.replace(" ", "-").lower()
        platform_data = random.choice(get_job_platforms())
        
        job = {
            "title": title,
            "company": co,
            "location": loc,
            "salary": sal,
            "platform": platform_data["name"],
            "posted": f"{random.randint(1, 23)}h ago",
            "url": platform_data["url"].format(query=encoded_query, query_dash=query_dash),
            "logo_url": fetch_company_logo_b64(co),
            "logo_fallback_url": get_company_logo_fallback(co),
        }
        jobs.append(job)
    return jobs

def get_job_platforms():
    return [
        {"name": "LinkedIn", "icon": "🔗", "url": "https://www.linkedin.com/jobs/search/?keywords={query}"},
        {"name": "Naukri", "icon": "🚀", "url": "https://www.naukri.com/{query_dash}-jobs"},
        {"name": "Indeed", "icon": "🎯", "url": "https://www.indeed.com/jobs?q={query}"},
        {"name": "Glassdoor", "icon": "🏢", "url": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query}"},
        {"name": "Unstop", "icon": "🏆", "url": "https://unstop.com/find/jobs?search={query}"},
        {"name": "Internshala", "icon": "🎓", "url": "https://internshala.com/internships/keywords-{query}"},
        {"name": "Foundit", "icon": "🔍", "url": "https://www.foundit.in/srp/results?query={query}"},
        {"name": "Google Jobs", "icon": "🌐", "url": "https://www.google.com/search?q=jobs+near+me+for+{query}"},
        {"name": "Oracle Jobs", "icon": "☁️", "url": "https://eeho.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/requisitions?keyword={query}"},
        {"name": "Amazon Jobs", "icon": "📦", "url": "https://www.amazon.jobs/en/search?base_query={query}"},
        {"name": "Google Careers", "icon": "🎨", "url": "https://www.google.com/about/careers/applications/jobs/results/?q={query}"},
        {"name": "Microsoft Jobs", "icon": "💻", "url": "https://careers.microsoft.com/us/en/search-results?q={query}"}
    ]

def generate_search_links(candidate_data):
    # Extract a search query based on skills or summary
    skills = candidate_data.get('skills', [])
    # Take top 3 tech skills for a focused search
    tech_skills = skills[:3]
    query_base = " ".join(tech_skills) if tech_skills else "Software Engineer"
    
    encoded_query = quote(query_base)
    query_dash = query_base.replace(" ", "-").lower()
    
    links = []
    for platform in get_job_platforms():
        final_url = platform['url'].format(query=encoded_query, query_dash=query_dash)
        links.append({
            "name": platform['name'],
            "icon": platform['icon'],
            "url": final_url
        })
    return links, query_base

def suggest_roles(skills, jd_text=""):
    # Map common skill sets to likely roles
    roles = []
    s_lower = [s.lower() for s in skills]
    jd_lower = jd_text.lower() if jd_text else ""
    
    if any(x in s_lower for x in ['python', 'django', 'flask', 'fastapi']) or "backend" in jd_lower or "python" in jd_lower: roles.append("Backend Developer")
    if any(x in s_lower for x in ['react', 'angular', 'vue', 'html', 'css']) or "frontend" in jd_lower or "react" in jd_lower: roles.append("Frontend Developer")
    if any(x in s_lower for x in ['machine learning', 'nlp', 'pytorch', 'tensorflow']) or "machine learning" in jd_lower: roles.append("AI/ML Engineer")
    if any(x in s_lower for x in ['aws', 'azure', 'docker', 'kubernetes']) or "devops" in jd_lower: roles.append("DevOps Engineer")
    if any(x in s_lower for x in ['sql', 'postgresql', 'tableau', 'pandas']) or "data analyst" in jd_lower: roles.append("Data Analyst")
    if "full stack" in jd_lower or "fullstack" in jd_lower: roles.append("Full Stack Developer")
    
    if not roles: roles = ["Software Development Engineer"]
    return list(set(roles))
