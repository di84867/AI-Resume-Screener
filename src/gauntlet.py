import random

# A mock database of 'hard' technical scenarios mapped to skills
SCENARIO_DB = {
    "python": [
        "Debug a memory leak in a long-running Celery worker process processing large datasets.",
        "Optimize a pandas dataframe operation that is currently taking 5 minutes to run on 1GB of data.",
        "Design a thread-safe singleton pattern for a database connection pool."
    ],
    "react": [
        "Investigate and fix unnecessary re-renders in a complex detailed dashboard grid.",
        "Implement a custom hook for handling WebSocket connections with automatic reconnection and exponential backoff.",
        "Migrate a legacy Class Component context provider to modern Redux Toolkit slices without breaking the API."
    ],
    "sql": [
        "Optimize a query involving three LEFT JOINs on non-indexed columns in a table with 10 million rows.",
        "Design a schema migration strategy for a zero-downtime deployment of a column rename.",
        "Debug a deadlock situation occurring during high-concurrency transaction updates."
    ],
    "aws": [
        "Architect a disaster recovery plan for an RDS database with a generic RPO of 5 minutes.",
        "Debug a Lambda function timeout issue when connecting to a VPC-bound ElastiCache instance.",
        "Secure an S3 bucket that needs to be accessed by a specific cross-account IAM role only."
    ],
    "machine learning": [
        "Diagnose why your model has high accuracy on training data but fails completely on the production test set (Concept Drift).",
        "Optimize the inference latency of a Transformer model running on a CPU-only edge device.",
        "Handle a class imbalance of 1:1000 in a fraud detection dataset without using synthetic oversampling."
    ],
    "java": [
        "Troubleshoot a 'OutOfMemoryError: Metaspace' in a Spring Boot application.",
        "Refactor a monolithic service into microservices, specifically handling distributed transactions (Saga Pattern)."
    ],
    "leadership": [
        "Your team is blocked by a dependency on another team that is 2 weeks late. How do you handle the stakeholder communication?",
        "Two senior engineers are in a deadlock over an architectural decision. How do you resolve the conflict?"
    ]
}

GENERIC_SCENARIOS = [
    "Describe a time you had to reverse-engineer a legacy system with no documentation.",
    "You production database just dropped all tables. What is your immediate reaction plan (Minutes 0-15)?",
    "Explain a complex technical concept to a non-technical stakeholder who is resisting the implementation."
]

def generate_challenge(candidate_data, jd_text=""):
    """
    Generates a 3-part 'Gauntlet' challenge based on the candidate's top skills.
    """
    name = candidate_data.get('name', 'Candidate')
    skills = candidate_data.get('skills', [])
    
    # Normalize skills to lower case for matching
    skills_lower = [s.lower() for s in skills]
    jd_lower = jd_text.lower()
    
    challenge_parts = []
    
    # 1. Technical Deep Dive (Based on top skill match)
    found_tech = False
    for skill, scenarios in SCENARIO_DB.items():
        if any(skill in s for s in skills_lower):
            question = random.choice(scenarios)
            challenge_parts.append(f"**Level 1: The Specialist Trap**\nIt's Day 1. The system is on fire. {question}")
            found_tech = True
            break
    
    if not found_tech:
        challenge_parts.append(f"**Level 1: The Audit**\n{random.choice(GENERIC_SCENARIOS)}")

    # 2. System Design / Architecture (Based on JD or skills)
    if "python" in jd_lower or "java" in jd_lower or "backend" in jd_lower:
        arch_challenge = "We need to scale our core service from 10k to 1M Daily Active Users. Our current monolithic SQL database is the bottleneck. Sketch a migration plan to NoSQL or Sharding while maintaining data consistency."
    elif "react" in jd_lower or "frontend" in jd_lower:
        arch_challenge = "Design the architecture for a highly interactive, real-time trading dashboard handling thousands of websocket events per second without crashing the browser."
    elif "machine learning" in jd_lower or "data science" in jd_lower:
        arch_challenge = "Design an ML pipeline for real-time fraud detection. How do you handle feature engineering, model serving latency, and CI/CD for model weights?"
    else:
        # Fallback to skills
        if "react" in skills_lower or "javascript" in skills_lower:
             arch_challenge = "Design the architecture for a highly interactive, real-time dashboard."
        else:
             arch_challenge = "We need to scale our core service from 10k to 1M Daily Active Users. Our current monolithic SQL database is the bottleneck."

    challenge_parts.append(f"**Level 2: The Architect's Dilemma**\n{arch_challenge}")

    # 3. Behavioral / Culture Check
    challenge_parts.append("**Level 3: The Culture Fit**\n"
                           "A product manager demands a feature release by Friday that you know is security-compromised. "
                           "They say 'Just ship it, we fix it later.' specific to your experience, how do you handle this?")
                           
    return "\n\n".join(challenge_parts)

