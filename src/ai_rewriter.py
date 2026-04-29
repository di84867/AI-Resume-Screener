"""
ai_rewriter.py
--------------
LangChain-powered AI features:
  - Bullet Point Rewriter  (transform weak → strong STAR-method bullets)
  - AI Summary Optimizer   (rewrite professional summary)
  - Semantic Job-to-Resume scorer (LLM reasoning, not just embeddings)

Uses HuggingFace Inference API (free) as default — no API key needed.
Falls back to rule-based rewrites if LLM is unavailable.
"""

from __future__ import annotations

import os
import re
import random
from typing import Any, Dict, List, Optional

# ── LangChain imports (graceful fallback if package missing) ──────────────────
try:
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from langchain_huggingface import HuggingFaceEndpoint
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# ---------------------------------------------------------------------------
# Strong verb bank for rule-based fallback
# ---------------------------------------------------------------------------
STRONG_VERBS = [
    "Orchestrated", "Engineered", "Architected", "Spearheaded", "Optimized",
    "Accelerated", "Automated", "Deployed", "Delivered", "Scaled",
    "Leveraged", "Pioneered", "Transformed", "Streamlined", "Championed",
]

RESULT_PHRASES = [
    "resulting in a {pct}% improvement in performance",
    "reducing latency by {pct}%",
    "increasing throughput by {pct}x",
    "cutting operational costs by {pct}%",
    "improving user satisfaction scores by {pct}%",
]


def _random_metric():
    pct = random.randint(15, 45)
    phrase = random.choice(RESULT_PHRASES).format(pct=pct)
    return phrase


# ---------------------------------------------------------------------------
# LLM factory – picks the best available provider
# ---------------------------------------------------------------------------

def _get_llm(openai_api_key: Optional[str] = None, 
             hf_token: Optional[str] = None, 
             gemini_api_key: Optional[str] = None,
             provider: str = "OpenAI"):
    """Return the best available LLM chain component based on selected provider."""
    if not LANGCHAIN_AVAILABLE:
        return None

    # Option 1: OpenAI
    if provider == "OpenAI" and OPENAI_AVAILABLE and openai_api_key:
        try:
            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.4,
                openai_api_key=openai_api_key,
            )
        except Exception:
            pass

    # Option 2: Google Gemini
    if provider == "Gemini" and GEMINI_AVAILABLE and gemini_api_key:
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.4,
                google_api_key=gemini_api_key,
            )
        except Exception:
            pass

    # Option 3: HuggingFace (Fallback/Secondary)
    if provider == "HuggingFace" and HF_AVAILABLE:
        token = hf_token or os.environ.get("HF_TOKEN", "")
        if token:
            try:
                return HuggingFaceEndpoint(
                    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
                    huggingfacehub_api_token=token,
                    max_new_tokens=300,
                    temperature=0.4,
                )
            except Exception:
                pass

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def rewrite_bullet(
    bullet: str,
    context: str = "",
    openai_key: Optional[str] = None,
    hf_token: Optional[str] = None,
    gemini_key: Optional[str] = None,
    provider: str = "OpenAI",
) -> str:
    """
    Transform a weak bullet point into a metrics-driven, STAR-method bullet.
    Falls back to rule-based rewrite if no LLM is configured.
    """
    bullet = bullet.strip().lstrip("-•* ")
    if not bullet:
        return bullet

    llm = _get_llm(openai_key, hf_token, gemini_key, provider)
    if llm:
        prompt = PromptTemplate.from_template(
            "You are a professional resume writer. Rewrite the following weak resume "
            "bullet point into a strong, metrics-driven, STAR-method bullet. "
            "Use a powerful action verb and add a plausible quantitative result. "
            "Keep it to one concise sentence. Do not add placeholders like [X].\n\n"
            "Weak bullet: {bullet}\n"
            "Context (role/project): {context}\n\n"
            "Strong bullet (no leading dash):"
        )
        try:
            chain  = prompt | llm | StrOutputParser()
            result = chain.invoke({"bullet": bullet, "context": context})
            # Strip leading dashes/bullets from LLM output
            result = re.sub(r"^[-•*]\s*", "", result.strip())
            return result if result else _rule_based_rewrite(bullet)
        except Exception:
            pass

    return _rule_based_rewrite(bullet)


def _rule_based_rewrite(bullet: str) -> str:
    """Heuristic fallback: replace weak openers and append a metric."""
    weak_map = {
        "helped":              "Supported",
        "was responsible for": "Led",
        "worked on":           "Developed",
        "assisted":            "Facilitated",
        "participated in":     "Collaborated on",
        "did":                 "Executed",
        "made":                "Created",
        "used":                "Leveraged",
        "handled":             "Managed",
        "involved in":         "Contributed to",
    }
    lower = bullet.lower()
    for weak, strong in weak_map.items():
        if lower.startswith(weak):
            bullet = strong + bullet[len(weak):]
            break
    else:
        # Prepend a strong verb if none found
        first_word = bullet.split()[0] if bullet.split() else ""
        if not any(v.lower() == first_word.lower() for v in STRONG_VERBS):
            verb  = random.choice(STRONG_VERBS)
            bullet = f"{verb} {bullet[0].lower()}{bullet[1:]}"

    # Append metric if none present
    has_metric = bool(re.search(r"\d+%|\$\d+|\d+x", bullet))
    if not has_metric:
        bullet = bullet.rstrip(".,;") + ", " + _random_metric()

    return bullet


def optimize_summary(
    data: Dict[str, Any],
    target_role: str = "",
    openai_key: Optional[str] = None,
    hf_token: Optional[str] = None,
    gemini_key: Optional[str] = None,
    provider: str = "OpenAI",
) -> str:
    """
    Rewrite the professional summary using AI (or heuristic fallback).
    """
    current_summary = data.get("summary", "")
    skills          = ", ".join(data.get("skills", [])[:7])
    name            = data.get("name", "the candidate")

    llm = _get_llm(openai_key, hf_token, gemini_key, provider)
    if llm:
        prompt = PromptTemplate.from_template(
            "Rewrite this professional summary to be concise, impactful, and optimised for ATS "
            "and recruiters. Highlight the top skills and tailor for the role if provided. "
            "Keep it to 3–4 sentences.\n\n"
            "Name: {name}\n"
            "Current Summary: {summary}\n"
            "Top Skills: {skills}\n"
            "Target Role: {role}\n\n"
            "Rewritten Summary:"
        )
        try:
            chain = prompt | llm | StrOutputParser()
            result = chain.invoke({
                "name": name, "summary": current_summary,
                "skills": skills, "role": target_role,
            })
            if result and len(result) > 40:
                return result.strip()
        except Exception:
            pass

    # Fallback
    role_str = f" targeting a {target_role} role" if target_role else ""
    return (
        f"Results-driven professional{role_str} with expertise in {skills}. "
        "Demonstrated ability to deliver scalable solutions and drive measurable impact. "
        "Adept at collaborating cross-functionally to align technical strategies with business objectives."
    )


def rewrite_all_bullets(
    experience: List[Any],
    openai_key: Optional[str] = None,
    hf_token: Optional[str] = None,
    gemini_key: Optional[str] = None,
    provider: str = "OpenAI",
) -> List[Any]:
    """Batch-rewrite all bullet points. Supports both legacy List[str] and new List[Dict]."""
    rewritten_experience = []
    
    for item in experience:
        if isinstance(item, dict):
            # Structured Job Dict
            new_item = item.copy()
            bullets = item.get('bullets', [])
            improved_bullets = []
            for b in bullets:
                improved = rewrite_bullet(b, context=item.get('role', ''), openai_key=openai_key, hf_token=hf_token, gemini_key=gemini_key, provider=provider)
                improved_bullets.append(improved)
            new_item['bullets'] = improved_bullets
            rewritten_experience.append(new_item)
        else:
            # Legacy string format
            stripped = str(item).strip()
            if stripped.startswith(("-", "•", "*")):
                improved = rewrite_bullet(stripped.lstrip("-•* "), openai_key=openai_key, hf_token=hf_token, gemini_key=gemini_key, provider=provider)
                rewritten_experience.append(f"- {improved}")
            else:
                rewritten_experience.append(item)
                
    return rewritten_experience



def semantic_job_match_reasoning(
    resume_text: str,
    jd_text: str,
    openai_key: Optional[str] = None,
    hf_token: Optional[str] = None,
    gemini_key: Optional[str] = None,
    provider: str = "OpenAI",
) -> str:
    """
    Use an LLM to provide a human-readable explanation of how well the resume
    matches the JD — beyond embedding cosine similarity.
    """
    llm = _get_llm(openai_key, hf_token, gemini_key, provider)
    if llm:
        prompt = PromptTemplate.from_template(
            "You are an expert technical recruiter. Analyse the candidate's resume "
            "against the job description below and provide:\n"
            "1. A match score out of 10\n"
            "2. Top 3 strengths for this role\n"
            "3. Top 3 gaps or weaknesses\n"
            "4. One concrete recommendation the candidate should address\n\n"
            "JOB DESCRIPTION:\n{jd}\n\n"
            "RESUME:\n{resume}\n\n"
            "Analysis:"
        )
        try:
            chain = prompt | llm | StrOutputParser()
            result = chain.invoke({"jd": jd_text[:2000], "resume": resume_text[:3000]})
            return result.strip() if result else ""
        except Exception:
            pass
    return ""
