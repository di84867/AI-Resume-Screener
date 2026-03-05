import random
from urllib.parse import quote

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
        # Combine skills for descriptive title
        prefix = random.choice(["Senior", "Staff", "Lead", "Associate", "Cloud", "Neural"])
        title = f"{prefix} {main_role}"
        
        # Generate a realistic URL
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
            "url": platform_data["url"].format(query=encoded_query, query_dash=query_dash)
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

def suggest_roles(skills):
    # Map common skill sets to likely roles
    roles = []
    s_lower = [s.lower() for s in skills]
    
    if any(x in s_lower for x in ['python', 'django', 'flask', 'fastapi']): roles.append("Backend Developer")
    if any(x in s_lower for x in ['react', 'angular', 'vue', 'html', 'css']): roles.append("Frontend Developer")
    if any(x in s_lower for x in ['machine learning', 'nlp', 'pytorch', 'tensorflow']): roles.append("AI/ML Engineer")
    if any(x in s_lower for x in ['aws', 'azure', 'docker', 'kubernetes']): roles.append("DevOps Engineer")
    if any(x in s_lower for x in ['sql', 'postgresql', 'tableau', 'pandas']): roles.append("Data Analyst")
    
    if not roles: roles = ["Software Development Engineer"]
    return list(set(roles))
