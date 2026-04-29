import io
try:
    import spacy
    from spacy.matcher import Matcher
    from spacy.language import Language
    _SPACY_OK = True
except ImportError:
    _SPACY_OK = False

from typing import Any
from pypdf import PdfReader

# Expanded skill set for better matching
COMMON_SKILLS = [
    "python", "java", "c++", "javascript", "typescript", "html", "css", "react", "angular", "vue",
    "sql", "nosql", "postgresql", "mongodb", "redis", "aws", "azure", "gcp", "docker", "kubernetes",
    "git", "jenkins", "ci/cd", "machine learning", "deep learning", "nlp", "scikit-learn", "tensorflow",
    "pytorch", "pandas", "numpy", "matplotlib", "seaborn", "tableau", "power bi", "excel", "spark",
    "hadoop", "kafka", "flask", "django", "fastapi", "rest api", "graphql", "linux", "bash", "agile",
    "scrum", "jira", "communication", "teamwork", "problem solving", "leadership", "node.js", 
    "ruby", "rails", "php", "swift", "kotlin", "rust", "go", "golang"
]

def load_nlp() -> Any:
    """Load spaCy model with robust fallbacks."""
    if not _SPACY_OK:
        return None
    try:
        if not spacy.util.is_package("en_core_web_sm"):
             spacy.cli.download("en_core_web_sm")
        return spacy.load("en_core_web_sm")
    except Exception as e:
        print(f"[load_nlp] Warning: Could not load 'en_core_web_sm': {e}")
        try:
            # Fallback to blank English model if download fails
            return spacy.blank("en")
        except Exception:
            return None


def parse_resume(file_obj: Any) -> tuple[str, bool]:
    """Extract text from PDF and check for images (potential photos)."""
    text = ""
    has_image = False
    try:
        # Handle bytes input
        if isinstance(file_obj, bytes):
            file_obj = io.BytesIO(file_obj)
            
        reader = PdfReader(file_obj)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
            
            # Check for images (XObjects)
            if "/XObject" in page["/Resources"]:
                xObject = page["/Resources"]["/XObject"].get_object()
                for obj in xObject:
                    if xObject[obj]["/Subtype"] == "/Image":
                        has_image = True
                        break

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return "", False
        
    return text.strip(), has_image

def extract_features(text: str, nlp: Language) -> dict[str, Any]:
    """Extract sections from resume text by identifying headings and capturing blocks."""
    lines = [line.rstrip() for line in text.split('\n')]
    
    # Define heading keywords
    heading_map = {
        'summary': ['summary', 'profile', 'objective', 'about me', 'professional profile'],
        'experience': ['experience', 'work', 'employment', 'history', 'professional background'],
        'education': ['education', 'academic', 'qualification', 'certifications', 'studies'],
        'skills': ['skills', 'competencies', 'expertise', 'toolkit', 'technical skills', 'stack']
    }
    
    # Reverse mapping for quick lookup
    keyword_to_type = {}
    for stype, keywords in heading_map.items():
        for k in keywords:
            keyword_to_type[k] = stype

    sections = {}
    section_order = []
    current_stype = None
    current_lines = []
    
    # Track original headings found
    found_headings = {
        'summary': 'Professional Summary',
        'experience': 'Professional Experience',
        'education': 'Academic Credentials',
        'skills': 'Technical Skills'
    }

    # Heuristic for name: Usually first non-empty line
    candidate_name = None
    for line in lines:
        if line.strip():
            # Check if it looks like a name (short, capitalized)
            # Simple fallback for now
            if not candidate_name:
                # Use spaCy for better name detection on the first few lines
                doc_name = nlp(line)
                for ent in doc_name.ents:
                    if ent.label_ == "PERSON":
                        candidate_name = ent.text.strip()
                        break
                if not candidate_name and len(line.split()) <= 4:
                    candidate_name = line.strip()
            
            # Check if this line is a heading
            l_clean = line.strip().lower()
            if 0 < len(l_clean) < 50 and not l_clean.endswith(".") and not l_clean.startswith("-") and not l_clean.startswith("•"):
                is_heading = False
                for k in keyword_to_type:
                    if k in l_clean:
                        stype = keyword_to_type[k]
                        if stype not in sections: # Only catch first occurrence as heading
                            if current_stype:
                                sections[current_stype] = "\n".join(current_lines).strip()
                            
                            current_stype = stype
                            current_lines = []
                            section_order.append(stype)
                            found_headings[stype] = line.strip()
                            is_heading = True
                            break
                
                if is_heading: continue

            if current_stype:
                current_lines.append(line)
            elif not candidate_name:
                # Try to catch name if not already found
                pass

    # Save last section
    if current_stype:
        sections[current_stype] = "\n".join(current_lines).strip()

    # Fallback for Summary if not found as section (often at top without heading)
    if 'summary' not in sections:
        # Take first 300-500 chars after name before first heading
        sections['summary'] = text[:500].strip()

    # Extract Skills as list for visuals
    skills_text = sections.get('skills', "")
    doc_skills = nlp(skills_text.lower() if skills_text else text.lower())
    matcher = Matcher(nlp.vocab)
    skill_patterns = [[{"LOWER": word} for word in s.split()] if " " in s else [{"LOWER": s}] for s in COMMON_SKILLS]
    matcher.add("SKILL", skill_patterns)
    matches = matcher(doc_skills)
    extracted_skills = sorted(list(set([doc_skills[start:end].text.lower() for _, start, end in matches])))

    # --- Structured Parser Helpers ---
    def parse_structured_experience(lines: list[str]):
        objs = []
        current = None
        for line in lines:
            if not line: continue
            if line.strip().startswith(("-", "•", "*")):
                if current:
                    current["bullets"].append(line.lstrip("-•* ").strip())
            else:
                parts = [p.strip() for p in line.split("|")]
                obj = {
                    "company": parts[0] if len(parts) > 0 else "Company",
                    "role": parts[1] if len(parts) > 1 else "",
                    "date": parts[2] if len(parts) > 2 else "",
                    "bullets": []
                }
                objs.append(obj)
                current = obj
        return objs

    def parse_structured_education(lines: list[str]):
        objs = []
        for line in lines:
            if not line or line.strip().startswith(("-", "•", "*")): continue
            parts = [p.strip() for p in line.split("|")]
            objs.append({
                "school": parts[0] if len(parts) > 0 else "Institution",
                "degree": parts[1] if len(parts) > 1 else "Degree",
                "date": parts[2] if len(parts) > 2 else ""
            })
        return objs

    exp_lines = [line.strip() for line in sections.get('experience', "").split('\n') if line.strip()]
    edu_lines = [line.strip() for line in sections.get('education', "").split('\n') if line.strip()]

    return {
        'name': candidate_name or "Professional Candidate",
        'skills': extracted_skills,
        'experience': parse_structured_experience(exp_lines),
        'education': parse_structured_education(edu_lines),
        'summary': sections.get('summary', ""),
        'original_headings': found_headings,
        'section_order': section_order,
        'full_text': text,
        'raw_sections': sections 
    }