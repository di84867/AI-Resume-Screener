from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import Any

def rank_candidates(resume_data: dict[str, dict[str, Any]], job_description: str) -> list[tuple[str, float, dict[str, Any]]]:
    """Rank resumes against job description using TF-IDF cosine similarity and skill overlap."""
    if not resume_data:
        return []
    
    # 1. TF-IDF Similarity
    resume_texts = [data['full_text'] for data in resume_data.values()]
    all_texts = resume_texts + [job_description.lower()]
    
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    try:
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        # Cosine similarity between each resume (rows 0 to N-1) and JD (last row)
        similarities = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix[-1:]).flatten()
    except ValueError:
        # Handle case where vocabulary is empty or other errors
        similarities = np.zeros(len(resume_data))

    # 2. Skill Overlap Bonus
    jd_lower = job_description.lower()
    
    final_scores = []
    candidates = list(resume_data.keys())
    
    for i, candidate in enumerate(candidates):
        base_score = similarities[i]
        features = resume_data[candidate]
        skills = features.get('skills', [])
        
        # Calculate overlap
        # Check which of the candidate's skills appear in the JD
        skill_matches = [skill for skill in skills if skill in jd_lower]
        match_count = len(skill_matches)
        
        # Boost score based on skill matches (simple heuristic)
        # weight skill match 0.05 per skill, max 0.5 boost
        skill_boost = min(match_count * 0.05, 0.5) 
        
        final_score = base_score + skill_boost
        
        # Validation mapping
        percentage_score = min(int(final_score * 100), 100)
        if percentage_score >= 80:
            validation_label = 'Excellent Match'
        elif percentage_score >= 60:
            validation_label = 'Good Match'
        elif percentage_score >= 40:
            validation_label = 'Average Match'
        else:
            validation_label = 'Low Match'
            
        
        # Update features with match info for UI
        features['skill_matches'] = list(set(skill_matches))
        features['ats_validation'] = validation_label
        features['ats_score_percentage'] = percentage_score
        features['score_breakdown'] = {
            'Text Similarity': f"{base_score:.2f}",
            'Skill Boost': f"{skill_boost:.2f} ({match_count} matches)"
        }
        
        final_scores.append((candidate, final_score, features))
    
    # Sort by final score
    ranked = sorted(final_scores, key=lambda x: x[1], reverse=True)
    return ranked

def generate_questions(features: dict[str, Any]) -> list[str]:
    """Generate interview questions based on resume features."""
    questions = []
    
    skills = features.get('skills', [])
    experience = features.get('experience', [])
    education = features.get('education', [])
    
    # Skill-based questions (prioritize matched skills if available)
    matched_skills = features.get('skill_matches', [])
    top_skills = matched_skills[:3] if matched_skills else skills[:3]
    
    for skill in top_skills:
        questions.append(f"Can you verify your proficiency in {skill} and describe a challenging problem you solved using it?")
    
    # Experience-based
    if experience:
        # Pick the one with the biggest number of years if possible, or just the first
        questions.append(f"Your resume mentions: '{experience[0][:80]}...'. Can you elaborate on your specific role and impact?")
        questions.append("Describe a situation where you had to manage conflicting priorities in your previous roles.")

    # Education-based
    if education:
        edu_inst = education[0]
        questions.append(f"How has your background at {edu_inst} influenced your approach to technical problems?")
    
    # General/Behavioral
    questions.extend([
        "What is the most complex technical challenge you've faced recently?",
        "How do you handle feedback and code reviews?",
        "Describe a time you had to learn a new technology quickly."
    ])
    
    return questions[:7] # Return top 7