import json
import os
from datetime import datetime

HISTORY_FILE = "data/user_history.json"

def _load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_history(data):
    os.makedirs("data", exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def save_user_analysis(email: str, job_description: str, resume_name: str, match_score: float, ats_label: str):
    history = _load_history()
    if email not in history:
        history[email] = []
    
    entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "resume_name": resume_name,
        "match_score": match_score,
        "ats_label": ats_label,
        "job_description_snippet": job_description[:100] + "..." if len(job_description) > 100 else job_description
    }
    history[email].append(entry)
    _save_history(history)

def get_user_history(email: str):
    history = _load_history()
    return history.get(email, [])

def delete_user_history_entry(email: str, entry_id: str):
    history = _load_history()
    if email in history:
        history[email] = [e for e in history[email] if e["id"] != entry_id]
        _save_history(history)
        return True
    return False
