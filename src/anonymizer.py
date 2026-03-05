import re

def anonymize_candidate(candidate_data, candidate_id):
    """
    Creates an anonymized version of the candidate data.
    Masks Name, Email, Phone, and Photo.
    """
    anon_data = candidate_data.copy()
    
    # Mask Identity
    anon_data['name'] = f"Candidate {candidate_id}"
    anon_data['masked_name'] = True
    
    # Remove Photo
    if 'photo' in anon_data:
        anon_data['photo'] = None
    anon_data['has_original_photo'] = False
    
    # Scrub text for standard PII patterns (Email, Phone)
    # Simple regex for now - can be expanded with Spacy NER if needed
    if 'email' in anon_data:
        anon_data['email'] = "[REDACTED_EMAIL]"
    if 'phone' in anon_data:
        anon_data['phone'] = "[REDACTED_PHONE]"
        
    return anon_data

def apply_blind_mode(processed_data):
    """
    Returns a new dict with all candidates anonymized.
    """
    blind_data = {}
    for i, (name, data) in enumerate(processed_data.items(), 1):
        # Create a consistent ID based on the order or hash could be better, 
        # but for now enumerate is fine for the session
        blind_data[f"Candidate {i:03d}"] = anonymize_candidate(data, f"{i:03d}")
    return blind_data
