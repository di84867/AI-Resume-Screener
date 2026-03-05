
import streamlit as st
import pandas as pd
import os
from typing import List, Tuple, Dict
from datetime import datetime

def validate_inputs(uploaded_files, job_desc: str) -> bool:
    """Validate user inputs."""
    pass # logic in app directly often easier for UI feedback, but keeping valid
    if not uploaded_files:
        st.warning("⚠️ Please upload at least one PDF resume.")
        return False
    if not job_desc.strip():
        st.warning("⚠️ Please enter a job description.")
        return False
    return True

def save_to_csv(ranked: List[Tuple[str, float, Dict]], output_dir: str = 'outputs') -> str:
    """Save ranked candidates to CSV."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ranked_candidates_{timestamp}.csv"
    output_path = os.path.join(output_dir, filename)
    
    data = []
    for name, score, features in ranked:
        skills = ", ".join(features.get('skills', []))
        experience = "; ".join(features.get('experience', [])[:3])
        education = "; ".join(features.get('education', []))
        match_breakdown = str(features.get('score_breakdown', {}))
        
        data.append({
            'Candidate Name': name,
            'Match Score': f"{score:.4f}",
            'Skills Detected': skills,
            'Experience': experience,
            'Education': education,
            'Score Details': match_breakdown
        })
        
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    return output_path