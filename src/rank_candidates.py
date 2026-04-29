from typing import Any
import numpy as np

# --- Graceful import: prefer LangChain embeddings, fall back to TF-IDF ---
try:
    from langchain_huggingface import HuggingFaceEmbeddings
    _LANGCHAIN_OK = True
except ImportError:
    _LANGCHAIN_OK = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sk_cosine
    _SKLEARN_OK = True
except ImportError:
    _SKLEARN_OK = False


class EmbeddingCache:
    _instance = None

    @classmethod
    def get(cls):
        if not _LANGCHAIN_OK:
            return None
        if cls._instance is None:
            try:
                cls._instance = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            except Exception as e:
                print(f"[EmbeddingCache] Could not load model: {e}")
                cls._instance = None
        return cls._instance


def _tfidf_similarities(resume_texts: list, jd_text: str) -> "np.ndarray":
    """TF-IDF cosine-similarity fallback."""
    if not _SKLEARN_OK:
        return np.zeros(len(resume_texts))
    all_texts = resume_texts + [jd_text.lower()]
    vec = TfidfVectorizer(stop_words='english', max_features=5000)
    try:
        mat = vec.fit_transform(all_texts)
        return sk_cosine(mat[:-1], mat[-1:]).flatten()
    except Exception:
        return np.zeros(len(resume_texts))


def _flatten_structured_data(items: list[Any]) -> str:
    """Flatten structured experience/education into a single searchable string."""
    text_parts = []
    for item in items:
        if isinstance(item, dict):
            # Experience: company, role, date, bullets
            # Education: school, degree, date
            parts = [
                item.get('company', ''),
                item.get('role', ''),
                item.get('school', ''),
                item.get('degree', ''),
                item.get('date', ''),
                ' '.join(item.get('bullets', []))
            ]
            text_parts.append(' '.join([p for p in parts if p]))
        else:
            text_parts.append(str(item))
    return ' '.join(text_parts)


def rank_candidates(resume_data: dict, job_description: str, use_deep: bool = False) -> list:
    """Rank resumes against JD using semantic embeddings (if use_deep=True) or TF-IDF."""
    if not resume_data:
        return []

    resume_texts = []
    for data in resume_data.values():
        txt = (
            data.get('summary', '') + ' ' +
            _flatten_structured_data(data.get('experience', [])) + ' ' +
            _flatten_structured_data(data.get('education', [])) + ' ' +
            ' '.join(data.get('skills', []))
        )
        # Fallback to full text if extracted sections are sparse
        if not txt.strip() or len(txt.split()) < 10:
            txt = data.get('full_text', '')
        resume_texts.append(txt)

    # 1. Semantic similarity
    similarities = None
    if use_deep:
        emb_model = EmbeddingCache.get()
        if emb_model:
            try:
                jd_emb  = emb_model.embed_query(job_description)
                r_embs  = emb_model.embed_documents(resume_texts)
                sims    = []
                for r_emb in r_embs:
                    n = np.linalg.norm(jd_emb) * np.linalg.norm(r_emb)
                    sims.append(float(np.dot(jd_emb, r_emb) / n) if n else 0.0)
                similarities = np.array(sims)
            except Exception as e:
                print(f"[rank] Embedding error: {e}. Falling back to TF-IDF.")
        else:
            print("[rank] Embedding model not available. Falling back to TF-IDF.")
    
    if similarities is None:
        similarities = _tfidf_similarities(resume_texts, job_description)


    # 2. Skill Overlap Bonus
    jd_lower = job_description.lower()
    
    final_scores = []
    candidates = list(resume_data.keys())
    
    for i, candidate in enumerate(candidates):
        base_score = similarities[i]
        features = resume_data[candidate]
        skills = features.get('skills', [])
        
        # Calculate overlap
        skill_matches = [skill for skill in skills if skill in jd_lower]
        match_count = len(skill_matches)
        
        # Boost score based on skill matches (simple heuristic)
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
    experience = features.get('experience', []) # List of Dicts
    education = features.get('education', [])   # List of Dicts
    
    # Skill-based questions
    matched_skills = features.get('skill_matches', [])
    top_skills = matched_skills[:3] if matched_skills else skills[:3]
    
    for skill in top_skills:
        questions.append(f"Can you verify your proficiency in {skill} and describe a challenging problem you solved using it?")
    
    # Experience-based
    if experience and isinstance(experience[0], dict):
        exp0 = experience[0]
        comp = exp0.get('company', 'your previous role')
        role = exp0.get('role', 'your responsibilities')
        questions.append(f"Your resume mentions you worked as '{role}' at '{comp}'. Can you elaborate on your specific impact there?")
        questions.append("Describe a situation where you had to manage conflicting priorities in your previous roles.")
    elif experience:
        # Legacy fallback
        questions.append(f"Your resume mentions: '{str(experience[0])[:80]}...'. Can you elaborate on your specific impact?")

    # Education-based
    if education and isinstance(education[0], dict):
        edu0 = education[0]
        school = edu0.get('school', 'your educational institution')
        degree = edu0.get('degree', 'your studies')
        questions.append(f"How has your background in '{degree}' at '{school}' influenced your approach to technical problems?")
    elif education:
        # Legacy fallback
        questions.append(f"How has your background at '{str(education[0])}' influenced your approach?")
    
    # General/Behavioral
    questions.extend([
        "What is the most complex technical challenge you've faced recently?",
        "How do you handle feedback and code reviews?",
        "Describe a time you had to learn a new technology quickly."
    ])
    
    return questions[:7]
 # Return top 7