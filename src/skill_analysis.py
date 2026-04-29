"""
skill_analysis.py
-----------------
Advanced NLP pipeline for:
  - Keyword Gap Analysis (contextual missing vs. found)
  - Implicit Skill Extraction (infer hidden skills from mentioned tech)
  - Bias Detection (graduation years, gendered language, location flags)
  - Credential Consistency / Sanity Check (date overlaps)
"""

import re
from typing import Any, Dict, List, Tuple, Optional

# ---------------------------------------------------------------------------
# Implicit skill taxonomy
# ---------------------------------------------------------------------------
IMPLICIT_SKILL_MAP: Dict[str, List[str]] = {
    "kubernetes":        ["Cloud Native", "Containerization", "DevOps", "Orchestration"],
    "docker":            ["Containerization", "Cloud Native", "DevOps"],
    "terraform":         ["Infrastructure as Code", "Cloud Automation", "DevOps"],
    "aws":               ["Cloud Computing", "Distributed Systems"],
    "azure":             ["Cloud Computing", "Distributed Systems"],
    "gcp":               ["Cloud Computing", "Distributed Systems"],
    "spark":             ["Big Data", "Distributed Computing", "Data Engineering"],
    "kafka":             ["Event Streaming", "Distributed Systems", "Data Engineering"],
    "hadoop":            ["Big Data", "Data Engineering"],
    "tensorflow":        ["Machine Learning", "Deep Learning", "AI Engineering"],
    "pytorch":           ["Machine Learning", "Deep Learning", "AI Engineering"],
    "scikit-learn":      ["Machine Learning", "Data Science"],
    "pandas":            ["Data Analysis", "Data Science"],
    "numpy":             ["Numerical Computing", "Data Science"],
    "react":             ["Frontend Development", "Component Architecture", "SPA"],
    "angular":           ["Frontend Development", "SPA"],
    "vue":               ["Frontend Development", "SPA"],
    "graphql":           ["API Design", "Backend Development"],
    "rest api":          ["API Design", "Backend Development", "Web Services"],
    "fastapi":           ["API Development", "Backend Development"],
    "django":            ["Backend Development", "Web Development"],
    "flask":             ["Backend Development", "Web Development"],
    "postgresql":        ["Relational Databases", "Data Engineering"],
    "mongodb":           ["NoSQL Databases", "Data Engineering"],
    "redis":             ["Caching", "In-Memory Databases"],
    "git":               ["Version Control", "Collaborative Development"],
    "jenkins":           ["CI/CD", "DevOps", "Build Automation"],
    "ci/cd":             ["DevOps", "Build Automation", "Continuous Delivery"],
    "nlp":               ["Natural Language Processing", "AI Engineering", "Text Mining"],
    "machine learning":  ["AI Engineering", "Predictive Modeling"],
    "deep learning":     ["AI Engineering", "Neural Networks"],
    "linux":             ["Systems Programming", "DevOps"],
    "bash":              ["Shell Scripting", "Automation"],
    "agile":             ["Project Management", "Iterative Development"],
    "scrum":             ["Agile Methodology", "Project Management"],
    "tableau":           ["Data Visualization", "Business Intelligence"],
    "power bi":          ["Data Visualization", "Business Intelligence"],
    "swift":             ["iOS Development", "Mobile Development"],
    "kotlin":            ["Android Development", "Mobile Development"],
}

# ---------------------------------------------------------------------------
# Gendered / biased language patterns
# ---------------------------------------------------------------------------
GENDERED_TERMS = [
    r"\b(he|him|his|she|her|hers)\b",
    r"\bgentleman\b", r"\blady\b", r"\bmanpower\b",
    r"\bchairman\b", r"\bworkman\b", r"\bstewardess\b",
]

BIAS_TRIGGERS = {
    "graduation_year":      r"\b(19|20)\d{2}\b",        # Any 4-digit year might expose age
    "exact_birthday":       r"\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b",
    "marital_status":       r"\b(married|single|divorced|widowed)\b",
    "religion":             r"\b(muslim|christian|hindu|sikh|jewish|buddhist)\b",
    "nationality_bias":     r"\b(nationality|citizen|visa|work permit)\b",
    "gendered_language":    r"|".join(GENDERED_TERMS),
}

# ---------------------------------------------------------------------------
# STAR-method strong action verbs
# ---------------------------------------------------------------------------
STRONG_VERBS = {
    "Achieved", "Accelerated", "Architected", "Automated", "Championed",
    "Collaborated", "Conceptualized", "Consolidated", "Crafted", "Delivered",
    "Deployed", "Designed", "Developed", "Drove", "Engineered", "Enhanced",
    "Established", "Executed", "Expanded", "Facilitated", "Generated",
    "Grew", "Implemented", "Improved", "Increased", "Initiated", "Innovated",
    "Launched", "Led", "Leveraged", "Managed", "Maximized", "Mentored",
    "Migrated", "Optimized", "Orchestrated", "Overhauled", "Pioneered",
    "Produced", "Reduced", "Revamped", "Scaled", "Secured", "Simplified",
    "Spearheaded", "Streamlined", "Strengthened", "Transformed", "Upgraded",
}

WEAK_VERB_MAP = {
    "helped":             "Supported",
    "was responsible for": "Led",
    "worked on":          "Developed",
    "assisted":           "Facilitated",
    "took part in":       "Contributed to",
    "did":                "Executed",
    "made":               "Created",
    "used":               "Leveraged",
    "tried":              "Attempted to optimize",
    "handled":            "Managed",
    "involved in":        "Contributed to",
    "participated in":    "Collaborated on",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_implicit_skills(skills: List[str]) -> List[str]:
    """Given a list of explicit skills, return inferred 'hidden' skills."""
    inferred = set()
    lower_skills = {s.lower() for s in skills}
    for skill_key, implied in IMPLICIT_SKILL_MAP.items():
        if skill_key in lower_skills:
            inferred.update(implied)
    return sorted(inferred)


def keyword_gap_analysis(
    candidate_data: Dict[str, Any],
    jd_text: str,
    openai_key: Optional[str] = None,
    hf_token: Optional[str] = None,
    gemini_key: Optional[str] = None,
    provider: str = "OpenAI",
) -> Dict[str, Any]:
    """
    Advanced Semantic Gap Analysis.
    Deconstructs JD into competency areas and scans for 'clues' in the resume.
    """
    jd_lower = jd_text.lower()
    full_text = candidate_data.get("full_text", "")
    
    from src.ai_rewriter import _get_llm
    llm = _get_llm(openai_key, hf_token, gemini_key, provider)
    
    requirements: List[Dict[str, Any]] = []
    
    if llm:
        from langchain_core.prompts import PromptTemplate
        # Phase 1: High-level Requirement Extraction
        req_prompt = PromptTemplate.from_template(
            "Extract the top 10 core requirement areas from this Job Description. "
            "For each area, specify 3-5 sub-keywords or 'clues' that would indicate a match. "
            "Return as JSON list: [{\"area\": \"...\", \"clues\": [\"...\", \"...\"]}, ...]\n\n"
            "JD: {jd}"
        )
        try:
            res = llm.invoke(req_prompt.format(jd=jd_text[:2500]))
            import json
            # Clean markdown code block syntax if present
            txt = res.content if hasattr(res, 'content') else str(res)
            
            # Find the JSON part safely
            if "```json" in txt:
                txt = txt.split("```json")[-1].split("```")[0].strip()
            elif "```" in txt:
                txt = txt.split("```")[-1].split("```")[0].strip()
                
            match = re.search(r"\[[\s\S]*\]", txt)
            if match:
                requirements = json.loads(match.group(0))
        except Exception as e:
            print(f"[skill_analysis] JSON parse error: {e}. Falling back to implicit.")

    # Fallback to keyword-based if LLM fails or is unavailable
    if not requirements:
        # Use existing IMPLICIT_SKILL_MAP to build basic requirements
        for skill, clues in IMPLICIT_SKILL_MAP.items():
            if skill in jd_lower:
                requirements.append({"area": skill.title(), "clues": clues + [skill]})

    found_areas = []
    missing_areas = []
    
    # Phase 2: Evidence Scanning
    for req in requirements:
        area = req['area']
        clues = req['clues']
        
        # Check for any clue in the full text (with fuzzy intent if LLM available)
        detected_clue = None
        for clue in clues:
            if re.search(rf"\b{re.escape(clue.lower())}\b", full_text.lower()):
                detected_clue = clue
                break
        
        if detected_clue:
            found_areas.append({"area": area, "evidence": detected_clue})
        else:
            missing_areas.append(area)

    # Generate suggestions for missing areas
    suggestions = _generate_gap_suggestions(
        candidate_data, 
        missing_areas[:5],
        openai_key=openai_key,
        hf_token=hf_token,
        gemini_key=gemini_key,
        provider=provider
    )

    return {
        "found": found_areas,
        "missing": missing_areas,
        "suggestions": suggestions,
        "implicit": extract_implicit_skills(candidate_data.get("skills", [])),
    }


def _generate_gap_suggestions(
    candidate_data: Dict[str, Any],
    missing_keywords: List[str],
    openai_key: Optional[str] = None,
    hf_token: Optional[str] = None,
    gemini_key: Optional[str] = None,
    provider: str = "OpenAI",
) -> List[str]:
    """
    For each missing keyword, generate a contextual bullet-point suggestion
    drawing from the candidate's existing experience.
    """
    if not missing_keywords:
        return []

    from src.ai_rewriter import _get_llm
    llm = _get_llm(openai_key, hf_token, gemini_key, provider)
    
    existing_skills = candidate_data.get("skills", [])
    top_existing = ", ".join(existing_skills[:3]) if existing_skills else "your core competencies"
    
    if llm:
        from langchain_core.prompts import PromptTemplate
        prompt = PromptTemplate.from_template(
            "The candidate is applying for a role but is missing the following technical keywords: {keywords}. "
            "The candidate already has experience with: {existing}. "
            "Generate 5 distinct, professional resume bullet point suggestions (one for each missing keyword) "
            "that show how they could bridge the gap or apply their existing skills to these areas. "
            "Format: One suggestion per line, starting with 'Add a bullet like: ...'. "
            "Keep them concise and action-oriented."
        )
        try:
            response = llm.invoke(prompt.format(keywords=", ".join(missing_keywords), existing=top_existing))
            content = response.content if hasattr(response, 'content') else str(response)
            ai_suggestions = [line.strip() for line in content.split("\n") if "Add a bullet like" in line]
            if ai_suggestions:
                return ai_suggestions[:len(missing_keywords)]
        except Exception:
            pass

    # Diverse Fallback Templates (Avoid repetition)
    templates = [
        'Add a bullet like: "Leveraged {existing} alongside {kw} to [describe a measurable outcome]" to highlight your adjacent competency.',
        'Add a bullet like: "Architected a new solution using {kw} in conjunction with {existing} for [target benefit]" to demonstrate cross-functional expertise.',
        'Add a bullet like: "Pioneered the integration of {kw} into existing workflows primarily driven by {existing}, resulting in [specific achievement]" to showcase adaptability.',
        'Add a bullet like: "Streamlined performance by applying {existing} principles to a new {kw}-based environment, achieving [measurable metric]" to prove technical versatility.',
        'Add a bullet like: "Collaborated on the deployment of {kw} systems while maintaining core {existing} infrastructure" to show end-to-end involvement.',
    ]
    
    suggestions = []
    import random
    for idx, kw in enumerate(missing_keywords):
        tmpl = templates[idx % len(templates)]
        suggestions.append(tmpl.format(existing=top_existing, kw=kw.title()))
        
    return suggestions


def detect_bias(full_text: str) -> List[Dict[str, str]]:
    """
    Scan resume text for potential bias triggers.
    Returns a list of {type, match, suggestion} dicts.
    """
    flags = []
    text_lower = full_text.lower()
    for bias_type, pattern in BIAS_TRIGGERS.items():
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            deduplicated = list(set(matches))[:3]
            flags.append({
                "type":       bias_type.replace("_", " ").title(),
                "match":      ", ".join(str(m) for m in deduplicated),
                "suggestion": _bias_suggestion(bias_type),
            })
    return flags


def _bias_suggestion(bias_type: str) -> str:
    suggestions = {
        "graduation_year":      "Consider removing graduation year to avoid age profiling.",
        "exact_birthday":       "Remove full date of birth — only graduation year (or none) is needed.",
        "marital_status":       "Omit marital status as it is irrelevant to professional competences.",
        "religion":             "Remove religious affiliations to maintain a neutral presentation.",
        "nationality_bias":     "Avoid mentioning visa/nationality unless specifically required by the role.",
        "gendered_language":    "Replace gendered pronouns/terms with gender-neutral alternatives.",
    }
    return suggestions.get(bias_type, "Review this section for potential bias.")


def sanity_check(candidate_data: Dict[str, Any]) -> List[str]:
    """
    Detect date overlaps and inconsistent credential timelines.
    Returns a list of human-readable warnings.
    """
    warnings: List[str] = []
    full_text = candidate_data.get("full_text", "")
    experience = candidate_data.get("experience", [])

    # Extract year pairs (start – end) from experience
    year_ranges: List[Tuple[int, int]] = []
    year_pattern = re.compile(r"(20\d{2})\s*[–\-–to]+\s*(20\d{2}|present|current)", re.IGNORECASE)
    
    # Process both structured and unstructured content
    search_targets = [full_text]
    for exp in experience:
        if isinstance(exp, dict):
            # Use explicit date field + bullets
            search_targets.append(exp.get('date', ''))
            search_targets.extend(exp.get('bullets', []))
        else:
            search_targets.append(str(exp))

    for target in search_targets:
        if not isinstance(target, str): continue
        for m in year_pattern.finditer(target):
            start_yr = int(m.group(1))
            end_str  = m.group(2).lower()
            end_yr   = 2025 if "present" in end_str or "current" in end_str else int(end_str)
            year_ranges.append((start_yr, end_yr))

    # Check overlaps
    year_ranges.sort(key=lambda x: x[0])
    for i in range(1, len(year_ranges)):
        prev_start, prev_end = year_ranges[i - 1]
        curr_start, curr_end = year_ranges[i]
        if curr_start < prev_end:
            warnings.append(
                f"⚠️ Date overlap detected: {prev_start}–{prev_end} overlaps with "
                f"{curr_start}–{curr_end}. Verify both roles are not claimed as full-time simultaneously."
            )

    # Future date check
    current_year = 2025
    for target in search_targets:
        if not isinstance(target, str): continue
        for m in re.finditer(r"(20\d{2})", target):
            yr = int(m.group(1))
            if yr > current_year + 1:
                warnings.append(
                    f"⚠️ Future date '{yr}' found in experience. Verify this is intentional."
                )
                break

    return warnings


def grade_bullet_points(experience: List[Any]) -> List[Dict[str, Any]]:
    """
    Grade each bullet. Supports both legacy List[str] and new List[Dict].
    Returns a list of grading dicts.
    """
    graded = []
    metric_pattern = re.compile(r"\d+%|\$\d+|\d+x|\d+\s*(million|billion|users|customers|hours|ms|requests)", re.IGNORECASE)

    # Flatten structured experience into individual bullets for grading
    all_bullets = []
    for item in experience:
        if isinstance(item, dict):
            all_bullets.extend(item.get('bullets', []))
        else:
            all_bullets.append(str(item))

    for line in all_bullets:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Strip bullet chars
        clean = re.sub(r"^[-•*]\s*", "", line)
        first_word = clean.split()[0].rstrip(".,:;") if clean.split() else ""

        verb_strength = "Missing"
        suggestion = ""
        if first_word.title() in STRONG_VERBS:
            verb_strength = "Strong ✅"
        elif first_word.lower() in WEAK_VERB_MAP:
            verb_strength = "Weak ⚠️"
            suggestion = f'Replace "{first_word}" with "{WEAK_VERB_MAP[first_word.lower()]}"'
        elif first_word:
            verb_strength = "Moderate 🔶"

        has_metric   = bool(metric_pattern.search(clean))
        star_score   = 0
        star_reasons = []

        if any(kw in clean.lower() for kw in ["at ", "for ", "while ", "during ", "within "]):
            star_score += 1
            star_reasons.append("Context ✅")
        else:
            star_reasons.append("Context ➖")

        if first_word.title() in STRONG_VERBS or verb_strength != "Missing":
            star_score += 2
            star_reasons.append("Action ✅")
        else:
            star_reasons.append("Action ❌")

        if has_metric:
            star_score += 2
            star_reasons.append("Result/Metric ✅")
        elif any(kw in clean.lower() for kw in ["resulting in", "leading to", "achieved", "increased", "reduced", "improved"]):
            star_score += 1
            star_reasons.append("Result ⚠️")
        else:
            star_reasons.append("Result ❌ (add a metric!)")

        star_label = (
            "Excellent" if star_score >= 4
            else "Good" if star_score == 3
            else "Fair" if star_score == 2
            else "Needs Work"
        )

        graded.append({
            "line":          line,
            "verb_strength": verb_strength,
            "suggestion":    suggestion,
            "has_metric":    has_metric,
            "star_score":    star_score,
            "star_label":    star_label,
            "star_reasons":  star_reasons,
        })

    return graded

