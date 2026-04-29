"""
latex_generator.py
------------------
ATS-Optimised LaTeX Resume Builder.

Features:
  - No-code JSON→LaTeX injection into templates
  - Multiple ATS-safe templates (article-based)
  - Section reordering logic
  - Expert-mode raw .tex export
  - Local pdflatex compilation via subprocess
"""

import os
import re
import subprocess
import tempfile
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _escape(text: str) -> str:
    """Escape LaTeX special characters robustly."""
    if not text:
        return ""
    text = str(text)
    # Handle backslash first to prevent double-escaping
    text = text.replace("\\", r"\textbackslash{}")
    chars = {
        "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}", "<": r"\textless{}", ">": r"\textgreater{}"
    }
    for ch, rep in chars.items():
        text = text.replace(ch, rep)
    return text


def _split_right_aligned(text: str):
    """Detect trailing date/location for right-alignment."""
    match = re.search(
        r"\s+((?:Expected\s)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"[a-z]*\s\d{4}.*|\d{4}\s*[-–]\s*(?:\d{4}|Present|present).*"
        r"|(?:Expected\s)?\d{4}|[A-Za-z]+,\s[A-Za-z]+)$",
        text,
        re.IGNORECASE,
    )
    if match:
        return text[: match.start()].strip(), match.group(1).strip()
    return text, ""


# ---------------------------------------------------------------------------
# Core template builders
# ---------------------------------------------------------------------------

_PREAMBLE = r"""
\documentclass[10pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage[margin=0.55in, top=0.45in, bottom=0.45in]{{geometry}}
\usepackage{{hyperref}}
\usepackage{{titlesec}}
\usepackage{{enumitem}}
\usepackage{{xcolor}}
\usepackage{{multicol}}
\usepackage{{microtype}}

\definecolor{{accent}}{{HTML}}{{{accent_color}}}

\hypersetup{{
    colorlinks=true, urlcolor=accent, linkcolor=accent, pdfborder={{0 0 0}}
}}

\titleformat{{\section}}{{\bfseries\large\color{{accent}}\uppercase}}{{}}{{0pt}}{{}}[\color{{accent}}\titlerule]
\titlespacing*{{\section}}{{0pt}}{{1.2ex}}{{0.8ex}}

\setlist[itemize]{{noitemsep, partopsep=0pt, topsep=2pt, leftmargin=1.4em}}
\pagestyle{{empty}}
"""

def _header_block(data: Dict[str, Any]) -> str:
    name   = _escape(data.get("name", "Your Name"))
    phone  = _escape(data.get("phone", ""))
    email  = _escape(data.get("email", ""))
    linkedin = data.get("linkedin", "")
    github   = data.get("github", "")

    contact_parts = []
    if phone:    contact_parts.append(phone)
    if email:    contact_parts.append(r"\href{mailto:" + email + r"}{" + email + r"}")
    if linkedin: contact_parts.append(r"\href{" + linkedin + r"}{LinkedIn}")
    if github:   contact_parts.append(r"\href{" + github + r"}{GitHub}")

    contact_line = r" $|$ ".join(contact_parts)
    return (
        r"\begin{center}" + "\n"
        r"  {\Huge \textbf{" + name + r"}}\\" + "\n"
        r"  \vspace{3pt}" + "\n"
        r"  \small " + contact_line + "\n"
        r"\end{center}" + "\n"
        r"\vspace{-6pt}" + "\n"
    )


def _summary_section(label: str, text: str) -> str:
    if not text:
        return ""
    return (
        r"\section{" + _escape(label) + "}\n"
        r"\noindent " + _escape(text) + "\n\n"
    )


def _skills_section(label: str, skills: List[str]) -> str:
    if not skills:
        return ""
    escaped = [_escape(s) for s in skills]
    # Split into two columns for readability
    half = max(1, len(escaped) // 2)
    col1 = escaped[:half]
    col2 = escaped[half:]
    rows = []
    for a, b in zip(col1, col2):
        rows.append(f"    \\item \\textbf{{{a}}}" + (f" & \\textbf{{{b}}}" if b else ""))
    if len(col1) > len(col2) and col1:
        rows.append(f"    \\item \\textbf{{{col1[-1]}}}")
    body = (
        r"\section{" + _escape(label) + "}\n"
        r"\begin{itemize}" + "\n"
    )
    for s in escaped:
        body += f"  \\item {s}\n"
    body += r"\end{itemize}" + "\n\n"
    return body


def _experience_section(label: str, items: List[Any]) -> str:
    if not items:
        return ""
    lines = [r"\section{" + _escape(label) + "}"]
    in_itemize = False
    for item in items:
        if not item: continue
        
        # New Structured Format
        if isinstance(item, dict):
            if in_itemize:
                lines.append(r"\end{itemize}")
                in_itemize = False
            
            comp = _escape(item.get("company", ""))
            role = _escape(item.get("role", ""))
            date = _escape(item.get("date", ""))
            loc  = _escape(item.get("location", ""))
            
            header = f"\\textbf{{{comp}}}"
            if role: header += f" $|$ \\textit{{{role}}}"
            if date: header += f" \\hfill \\textit{{{date}}}"
            lines.append(r"\noindent " + header)
            
            bullets = item.get("bullets", [])
            if bullets:
                lines.append(r"\begin{itemize}")
                for b in bullets:
                    lines.append(f"  \\item {_escape(b)}")
                lines.append(r"\end{itemize}")
            else:
                lines.append(r"\vspace{0.5ex}")
            continue

        # Legacy String Format
        raw = str(item).strip()
        if raw.startswith(("-", "•", "*")):
            clean = _escape(raw.lstrip("-•* ").strip())
            if not in_itemize:
                lines.append(r"\vspace{-1.2ex}")
                lines.append(r"\begin{itemize}")
                in_itemize = True
            lines.append(f"  \\item {clean}")
        else:
            if in_itemize:
                lines.append(r"\end{itemize}")
                in_itemize = False
            parts = [p.strip() for p in raw.split("|")]
            if len(parts) >= 2:
                company    = _escape(parts[0])
                role_raw   = parts[1]
                role, date = _split_right_aligned(role_raw)
                if len(parts) >= 3:
                    date = _escape(parts[2])
                lines.append(r"\noindent")
                lines.append(f"\\textbf{{{company}}} $|$ \\textit{{{role}}} \\hfill \\textit{{{date}}}")
            else:
                left, right = _split_right_aligned(parts[0])
                lines.append(r"\noindent")
                lines.append(f"\\textbf{{{_escape(left)}}} \\hfill \\textit{{{_escape(right)}}}")
    if in_itemize:
        lines.append(r"\end{itemize}")
    lines.append("")
    return "\n".join(lines) + "\n"



def _education_section(label: str, items: List[Any]) -> str:
    if not items:
        return ""
    lines = [r"\section{" + _escape(label) + "}"]
    in_itemize = False
    for item in items:
        if not item: continue
        
        # New Structured Format
        if isinstance(item, dict):
            if in_itemize:
                lines.append(r"\end{itemize}")
                in_itemize = False
            
            school = _escape(item.get("school", ""))
            degree = _escape(item.get("degree", ""))
            date   = _escape(item.get("date", ""))
            
            lines.append(r"\noindent")
            lines.append(f"\\textbf{{{school}}} \\hfill {date} \\\\")
            lines.append(f"\\textit{{{degree}}} \\\\[2pt]")
            continue

        # Legacy String Format
        raw = str(item).strip()
        if raw.startswith(("-", "•", "*")):
            clean = _escape(raw.lstrip("-•* ").strip())
            if not in_itemize:
                lines.append(r"\vspace{-1.2ex}")
                lines.append(r"\begin{itemize}")
                in_itemize = True
            lines.append(f"  \\item {clean}")
        else:
            if in_itemize:
                lines.append(r"\end{itemize}")
                in_itemize = False
            parts = [p.strip() for p in raw.split("|")]
            if len(parts) >= 2:
                school  = _escape(parts[0])
                degree  = _escape(parts[1])
                date    = _escape(parts[2]) if len(parts) >= 3 else ""
                lines.append(r"\noindent")
                lines.append(f"\\textbf{{{school}}} \\hfill {date} \\\\")
                lines.append(f"\\textit{{{degree}}} \\\\[2pt]")
            else:
                left, right = _split_right_aligned(parts[0])
                lines.append(r"\noindent")
                lines.append(f"\\textbf{{{_escape(left)}}} \\hfill \\textit{{{_escape(right)}}} \\\\[2pt]")
    if in_itemize:
        lines.append(r"\end{itemize}")
    lines.append("")
    return "\n".join(lines) + "\n"

def _generic_section(label: str, content: Any) -> str:
    if not content:
        return ""
    lines = [r"\section{" + _escape(label) + "}"]
    if isinstance(content, list):
        lines.append(r"\begin{itemize}")
        for item in content:
            lines.append(f"  \\item {_escape(str(item))}")
        lines.append(r"\end{itemize}")
    else:
        lines.append(r"\noindent " + _escape(str(content)))
    return "\n".join(lines) + "\n\n"



# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

LATEX_TEMPLATES = {
    "ATS Classic":    {"accent": "000000", "desc": "Maximum ATS compatibility. Black & white, article class."},
    "Teal Professional": {"accent": "0D9488", "desc": "Modern teal accent with clean layout."},
    "Royal Blue":     {"accent": "1e3a8a", "desc": "Deep professional blue — great for finance & consulting."},
    "Silicon Violet": {"accent": "7c3aed", "desc": "Tech-forward violet accent for engineers."},
    "Emerald Sharp":  {"accent": "059669", "desc": "Clean green accent — popular in sustainability & science."},
    "Crimson Harvard":{"accent": "991b1b", "desc": "Traditional academic red — ideal for research roles."},
    "Carbon Dark":    {"accent": "171717", "desc": "Minimal monochrome — suits senior professionals."},
}


def generate_latex(
    data: Dict[str, Any],
    template_name: str = "Teal Professional",
    section_order: Optional[List[str]] = None,
) -> str:
    """
    Generate a full .tex document from candidate data.

    Args:
        data          : candidate dict (name, email, phone, summary, skills, experience, education, …)
        template_name : key from LATEX_TEMPLATES
        section_order : ordered list like ['summary','experience','education','skills']
    """
    template = LATEX_TEMPLATES.get(template_name, LATEX_TEMPLATES["Teal Professional"])
    accent   = template["accent"]

    preamble = _PREAMBLE.format(accent_color=accent)

    h = data.get("original_headings", {})
    h_sum = h.get("summary", "Professional Summary")
    h_exp = h.get("experience", "Experience")
    h_edu = h.get("education", "Education")
    h_skl = h.get("skills", "Technical Skills")

    # Default section order
    if not section_order:
        stored = data.get("section_order", [])
        section_order = stored if stored else ["summary", "experience", "education", "skills"]
    # Ensure all exist
    for core in ["summary", "experience", "education", "skills"]:
        if core not in section_order:
            section_order.append(core)

    # --- Build body ---
    body = _header_block(data)

    seen = set()
    for sect in section_order:
        if sect in seen:
            continue
        seen.add(sect)
        
        # Core Sections
        if sect == "summary":
            body += _summary_section(h_sum, data.get("summary", ""))
        elif sect == "experience":
            body += _experience_section(h_exp, data.get("experience", []))
        elif sect == "education":
            body += _education_section(h_edu, data.get("education", []))
        elif sect == "skills":
            body += _skills_section(h_skl, data.get("skills", []))
        
        # Dynamic Generic Sections
        else:
            custom_label = h.get(sect, sect.title())
            # Prioritize content from custom_sections dict, fallback to root
            custom_content = data.get("custom_sections", {}).get(sect, data.get(sect, ""))
            body += _generic_section(custom_label, custom_content)


    return (
        preamble.strip()
        + "\n\n\\begin{document}\n\n"
        + body
        + "\n\\end{document}\n"
    )


def compile_latex_to_pdf(latex_code: str) -> bytes:
    """
    Compile a .tex string using pdflatex (must be installed via TeX Live).
    Returns raw PDF bytes, or b'' if compilation fails.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "resume.tex")
        pdf_path = os.path.join(tmpdir, "resume.pdf")

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_code)

        try:
            result = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-output-directory", tmpdir,
                    tex_path,
                ],
                capture_output=True,
                timeout=60,
                text=True,
            )
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    return f.read()
            # Try a second pass (for references/citations)
            subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-output-directory", tmpdir,
                    tex_path,
                ],
                capture_output=True,
                timeout=60,
            )
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    return f.read()
        except FileNotFoundError:
            pass  # pdflatex not installed — handled gracefully in UI
        except subprocess.TimeoutExpired:
            pass

    return b""


def is_pdflatex_available() -> bool:
    """Check if pdflatex is available on PATH."""
    try:
        r = subprocess.run(["pdflatex", "--version"], capture_output=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False
