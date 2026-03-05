from collections import Counter

def suggest_squad(processed_data, requirements):
    """
    Suggests a squad based on a list of role/skill requirements.
    requirements: list of strings (e.g. ['Python', 'React', 'Leadership'])
    
    Returns: typ. Dict[str, dict] -> { 'Role 1': CandidateData, ... }
    """
    squad = {}
    assigned_candidates = set() # To avoid cloning the same person
    
    # Helper to calculate score for a specific requirement
    def calculate_fit(candidate_skills, req):
        # precise match
        if req.lower() in [s.lower() for s in candidate_skills]:
            return 100
        # fuzzy / partial match could go here
        return 0

    for req in requirements:
        best_candidate = None
        best_score = -1
        
        for name, data in processed_data.items():
            if name in assigned_candidates:
                continue
                
            skills = data.get('skills', [])
            score = calculate_fit(skills, req)
            
            # Tie-breaker: total number of skills or length of experience
            # For now, just score
            if score > best_score and score > 0:
                best_score = score
                best_candidate = name
        
        if best_candidate:
            squad[req] = {
                'name': best_candidate, 
                'data': processed_data[best_candidate],
                'match_score': best_score
            }
            assigned_candidates.add(best_candidate)
        else:
            squad[req] = None # No match found
            
    return squad
