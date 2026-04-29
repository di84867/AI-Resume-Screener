
from typing import Dict, Any, List
import io
import json
import os
from xhtml2pdf import pisa

def generate_txt_resume(data: Dict[str, Any]) -> str:
    """Generate a clean, single-column plain text resume for ATS."""
    lines = []
    
    # 1. Contact Info
    name = data.get('name', 'CANDIDATE NAME')
    lines.append(name.upper())
    email = data.get('email', 'email@example.com')
    lines.append(email)
    lines.append("-" * max(len(name), len(email)))
    lines.append("")
    
    # Get custom headings
    h = data.get('original_headings', {})
    
    # 2. Add sections in ATS-friendly order
    s_order = data.get('section_order', ['summary', 'experience', 'education'])
    for core in ['summary', 'experience', 'education']:
        if core not in s_order: s_order.append(core)
        
    seen_sections = set()
    
    for sect in s_order:
        if sect in seen_sections: continue
        seen_sections.add(sect)
        
        if sect == 'summary' and data.get('summary'):
            lines.append(h.get('summary', 'PROFESSIONAL SUMMARY').upper())
            lines.append(data.get('summary'))
            lines.append("")
            
        elif sect == 'experience' and data.get('experience'):
            lines.append(h.get('experience', 'PROFESSIONAL EXPERIENCE').upper())
            for e in data.get('experience'):
                if isinstance(e, dict):
                    comp = e.get('company', '')
                    role = e.get('role', '')
                    date = e.get('date', '')
                    header = f"{comp} | {role} | {date}".strip(" |")
                    lines.append(header)
                    for b in e.get('bullets', []):
                        lines.append(f"  - {b}")
                else:
                    lines.append(f"- {e}")
            lines.append("")
            
        elif sect == 'education' and data.get('education'):
            lines.append(h.get('education', 'EDUCATION').upper())
            for ed in data.get('education'):
                if isinstance(ed, dict):
                    sch = ed.get('school', '')
                    deg = ed.get('degree', '')
                    date = ed.get('date', '')
                    lines.append(f"{sch} | {deg} | {date}".strip(" |"))
                else:
                    lines.append(f"- {ed}")
            lines.append("")

            
    # 3. Skills Always at the End for ATS Parsing
    if data.get('skills'):
        lines.append(h.get('skills', 'TECHNICAL SKILLS').upper())
        lines.append(", ".join(data.get('skills', [])))
        
    return "\n".join(lines).strip()

def generate_latex_resume(data: Dict[str, Any]) -> str:
    """Generate professional LaTeX resume code optimized for parsing and ATS, using the Ramit style."""
    name = data.get('name', 'CANDIDATE NAME')
    email = data.get('email', 'email@example.com')
    phone = data.get('phone', '+91-XXXXXXXXXX')
    linkedin = data.get('linkedin', 'https://linkedin.com/in/username')
    
    h = data.get('original_headings', {})
    h_sum = h.get('summary', 'Professional Summary')
    if len(h_sum) > 35: h_sum = 'Professional Summary'
    
    h_exp = h.get('experience', 'Experience / Internship')
    if len(h_exp) > 35: h_exp = 'Experience'
    
    h_edu = h.get('education', 'Education')
    if len(h_edu) > 35: h_edu = 'Education'
    
    h_skl = h.get('skills', 'Technical Skills')
    if len(h_skl) > 35: h_skl = 'Technical Skills'

    def escape_latex(text):
        if not text: return ""
        chars = ['&', '%', '$', '#', '_', '{', '}']
        for c in chars:
            text = text.replace(c, '\\' + c)
        return text

    latex_code = [
        r"\documentclass[11pt,a4paper]{article}",
        r"",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[margin=0.4in]{geometry}",
        r"\usepackage{hyperref}",
        r"\usepackage{titlesec}",
        r"\usepackage{enumitem}",
        r"\usepackage{xcolor}",
        r"",
        r"% --- Custom Styling ---",
        r"\hypersetup{",
        r"    colorlinks=true,",
        r"    linkcolor=blue,",
        r"    filecolor=magenta,      ",
        r"    urlcolor=black,",
        r"}",
        r"",
        r"\titleformat{\section}{\bfseries\large\uppercase}{}{0pt}{}[\titlerule]",
        r"\titlespacing*{\section}{0pt}{1.5ex}{1ex}",
        r"",
        r"\setlist[itemize]{noitemsep, partopsep=0pt, topsep=0pt, leftmargin=1.5em}",
        r"",
        r"\newcommand{\header}[4]{",
        r"    \begin{center}",
        r"        {\Huge \textbf{#1}} \\",
        r"        \vspace{2pt}",
        r"        \small #2 $|$ \href{mailto:#3}{#3} $|$ \href{#4}{LinkedIn}",
        r"    \end{center}",
        r"}",
        r"",
        r"% --- Document Content ---",
        r"\begin{document}",
        r"",
        f"\\header{{{escape_latex(name)}}}{{{escape_latex(phone)}}}{{{escape_latex(email)}}}{{{escape_latex(linkedin)}}}",
        r""
    ]
    
    import re

    def split_right_aligned(text):
        # Tries to find Dates or Locations at the end of the string to right-align them
        match = re.search(r'\s+((?:Expected\s)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{4}.*|\d{4}\s*-\s*\d{4}.*|(?:Expected\s)?\d{4}|[A-Za-z]+,\s[A-Za-z]+)$', text, re.IGNORECASE)
        if match:
            left = text[:match.start()].strip()
            right = match.group(1).strip()
            return left, right
        return text, ""

    s_order = data.get('section_order', ['summary', 'experience', 'education'])
    for core in ['summary', 'experience', 'education', 'skills']:
        if core not in s_order: s_order.append(core)
        
    seen = set()
    for sect in s_order:
        if sect in seen: continue
        seen.add(sect)
        
        if sect == 'summary' and data.get('summary'):
            summary_text = data.get('summary')
            latex_code.append(f"\\section{{{escape_latex(h_sum)}}}")
            latex_code.append(r"\noindent")
            latex_code.append(escape_latex(summary_text))
            latex_code.append("")
        
        elif sect == 'education' and data.get('education'):
            latex_code.append(f"\\section{{{escape_latex(h_edu)}}}")
            for ed in data.get('education'):
                if isinstance(ed, dict):
                    sch = escape_latex(ed.get('school', ''))
                    deg = escape_latex(ed.get('degree', ''))
                    date = escape_latex(ed.get('date', ''))
                    latex_code.append(r"\noindent")
                    latex_code.append(f"\\textbf{{{sch}}} \\hfill {date} \\\\")
                    latex_code.append(f"\\textit{{{deg}}} \\\\[1ex]")
                    continue

                ed_str = str(ed).strip()
                if not ed_str: continue
                parts = [p.strip() for p in ed_str.split('|')]
                if len(parts) >= 2:
                    school = escape_latex(parts[0])
                    degree = escape_latex(parts[1])
                    date = escape_latex(parts[2]) if len(parts) > 2 else ""
                    latex_code.append(r"\noindent")
                    latex_code.append(f"\\textbf{{{school}}} \\hfill {date} \\\\")
                    latex_code.append(f"\\textit{{{degree}}} \\\\[1ex]")
            latex_code.append("")
        
        elif sect == 'experience' and data.get('experience'):
            latex_code.append(f"\\section{{{escape_latex(h_exp)}}}")
            for item in data.get('experience'):
                if isinstance(item, dict):
                    comp = escape_latex(item.get('company', ''))
                    role = escape_latex(item.get('role', ''))
                    date = escape_latex(item.get('date', ''))
                    latex_code.append(r"\noindent")
                    latex_code.append(f"\\textbf{{{comp}}} $|$ \\textit{{{role}}} \\hfill \\textit{{{date}}}")
                    bullets = item.get('bullets', [])
                    if bullets:
                        latex_code.append(r"\begin{itemize}")
                        for b in bullets:
                            latex_code.append(f"    \\item {escape_latex(b)}")
                        latex_code.append(r"\end{itemize}")
                    latex_code.append(r"\vspace{1ex}")
                    continue

                it_str = str(item).strip()
                if not it_str: continue
                parts = [p.strip() for p in it_str.split('|')]
                if len(parts) >= 2:
                    comp = escape_latex(parts[0])
                    role = escape_latex(parts[1])
                    date = escape_latex(parts[2]) if len(parts) > 2 else ""
                    latex_code.append(r"\noindent")
                    latex_code.append(f"\\textbf{{{comp}}} $|$ \\textit{{{role}}} \\hfill \\textit{{{date}}} \\\\[1ex]")
            latex_code.append("")
            
        elif sect == 'skills' and data.get('skills'):
            latex_code.append(f"\\section{{{escape_latex(h_skl)}}}")
            latex_code.append(r"\begin{itemize}")
            skills = [escape_latex(s) for s in data.get('skills', [])]
            if len(skills) > 0:
                latex_code.append(f"    \\item \\textbf{{Core Competencies:}} {', '.join(skills)}")
            latex_code.append(r"\end{itemize}")
            latex_code.append("")
            
    latex_code.append(r"\end{document}")
    
    return "\n".join(latex_code)

TEMPLATE_FILE = "src/templates_registry.json"

def get_default_templates():
    return {
        "Executive Slate": {"desc": "Blue Sidebar, Pro Serif", "color": "#1e3a8a", "has_photo": True},
        "Aura Elite": {"desc": "Glassy Gradient Header", "color": "#6366F1", "has_photo": True},
        "Spectrum Pro": {"desc": "Modern Vertical Sidebar", "color": "#7c3aed", "has_photo": True},
        "Silicon Emerald": {"desc": "Top Border, Modern", "color": "#059669", "has_photo": False},
        "Harvard Classic": {"desc": "Traditional ATS", "color": "#991b1b", "has_photo": False},
        "Creative Royal": {"desc": "Vibrant Purple", "color": "#7c3aed", "has_photo": True},
        "Minimal Carbon": {"desc": "Dark Grey, Bold", "color": "#111827", "has_photo": False},
        "Standard Business": {"desc": "Safe Professional", "color": "#475569", "has_photo": False},
        "Clean Minimal": {"desc": "Strictly White", "color": "#000000", "has_photo": False},
        "ATS Titan": {"desc": "High Contrast Standard", "color": "#000000", "has_photo": False},
        "Quantum Chrono": {"desc": "Teal Timeline", "color": "#0f766e", "has_photo": False},
        "Glacier Simple": {"desc": "Blue Minimalist", "color": "#3b82f6", "has_photo": False},
        "Visionary Card": {"desc": "Bold Header Card", "color": "#8b5cf6", "has_photo": True},
        "Global Specialist": {"desc": "Dense Pro Sidebar", "color": "#1e40af", "has_photo": True},
        "Creative Grid": {"desc": "Modern Grid Layout", "color": "#ec4899", "has_photo": True},
        "Corporate Blue": {"desc": "Professional Corporate", "color": "#0f172a", "has_photo": True},
        "Infographic Flow": {"desc": "Visual Timeline", "color": "#10b981", "has_photo": True},
        "Nordic Clean": {"desc": "Minimalist White", "color": "#334155", "has_photo": True},
        "Silicon Vertex": {"desc": "Tech Geometric", "color": "#6366f1", "has_photo": False},
        "Arctic Blue": {"desc": "Cool & Professional ATS", "color": "#0891b2", "has_photo": False},
        "Midnight Pro": {"desc": "Dark Premium Header", "color": "#0f172a", "has_photo": True},
        "Minimalist Slate": {"desc": "Clean Text-Only", "color": "#334155", "has_photo": False},
        "Golden Executive": {"desc": "Gold Accents, Prestigious", "color": "#854d0e", "has_photo": True},
        "Azure Tech": {"desc": "Tech-Focused Layout", "color": "#0284c7", "has_photo": True}
    }

def get_templates():
    """Load templates from registry or return defaults."""
    defaults = get_default_templates()
    if os.path.exists(TEMPLATE_FILE):
        try:
            with open(TEMPLATE_FILE, 'r') as f:
                user_templates = json.load(f)
                for t_name, t_config in user_templates.items():
                    if t_name in defaults:
                        defaults[t_name].update(t_config)
                    else:
                        defaults[t_name] = t_config
                return defaults
        except:
            return defaults
    return defaults

def save_user_template(name: str, config: Dict[str, Any]):
    """Save or update a template in the registry."""
    templates = get_templates()
    templates[name] = config
    defaults = get_default_templates()
    user_only = {k: v for k, v in templates.items() if k not in defaults or v != defaults[k]}
    with open(TEMPLATE_FILE, 'w') as f:
        json.dump(user_only, f, indent=4)

def delete_user_template(name: str):
    """Remove a template from the user registry."""
    if not os.path.exists(TEMPLATE_FILE):
        return
    try:
        with open(TEMPLATE_FILE, 'r') as f:
            templates = json.load(f)
        if name in templates:
            del templates[name]
            with open(TEMPLATE_FILE, 'w') as f:
                json.dump(templates, f, indent=4)
    except:
        pass

def suggest_improvements(resume_features: Dict[str, Any], job_desc_text: str) -> Dict[str, Any]:
    suggestions = {'missing_skills': [], 'recommended_actions': [], 'section_improvements': {}}
    jd_lower = job_desc_text.lower()
    resume_skills = [s.lower() for s in resume_features.get('skills', [])]
    common_tech_keywords = ["python", "java", "c++", "javascript", "typescript", "html", "css", "react", "angular", "vue", "node.js", 
    "sql", "nosql", "postgresql", "mongodb", "redis", "aws", "azure", "gcp", "docker", "kubernetes",
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "pandas", "numpy", "power bi", "tableau", 
    "agile", "scrum", "communication", "leadership"]
    for keyword in common_tech_keywords:
        if keyword in jd_lower and keyword not in resume_skills:
            suggestions['missing_skills'].append(keyword)
    return suggestions

def optimize_summary(data: Dict[str, Any]) -> str:
    skills = data.get('skills', [])
    top_skills = ", ".join(skills[:5]) if skills else "various technical"
    return f"Dynamic professional with specialized expertise in {top_skills}. Proven track record of delivering high-quality solutions."

def generate_html_resume(data: Dict[str, Any], template: str = "Executive Slate", for_pdf: bool = False, thumbnail: bool = False) -> str:
    name = str(data.get('name') or 'CANDIDATE NAME').upper()
    summary = str(data.get('summary') or '')
    skills = data.get('skills') or []
    experience = data.get('experience') or []
    education = data.get('education') or []
    
    templates = get_templates()
    t_config = templates.get(template, templates["Executive Slate"])
    needs_photo = t_config.get('has_photo', False)
    photo_url = data.get('photo', None)
    if needs_photo and not photo_url:
        photo_url = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

    h = data.get('original_headings', {})
    h_sum = h.get('summary', 'Professional Summary')
    h_exp = h.get('experience', 'Professional Experience')
    h_edu = h.get('education', 'Academic Credentials')
    h_skl = h.get('skills', 'Technical Skills')
    custom_sects = data.get('custom_sections', {})

    # Harden CSS for xhtml2pdf compatibility
    base_font_size = "10pt" if for_pdf else "10pt"
    section_font_size = "12pt" if for_pdf else "13pt"
    
    page_css = ""
    if for_pdf:
        page_css = """
        @page { size: a4; margin: 1.25cm; }
        body { font-size: 10pt; line-height: 1.3; }
        """
    
    if thumbnail:
        container_style = "width: 850px; margin: 0; background: white; transform: scale(0.2); transform-origin: top left;"
    else:
        container_style = "width: 100%;" if for_pdf else "max-width: 850px; width: 100%; margin: 40px auto; background: white; box-shadow: 0 0 20px rgba(0,0,0,0.1); border-radius: 4px;"

    common_style = f"""
        {page_css}
        body {{ font-family: 'Helvetica', 'Arial', sans-serif; line-height: 1.5; color: #111; margin: 0; padding: 0; }}
        h1, h2, h3 {{ margin: 0; padding: 0; }}
        ul {{ padding-left: 22px; list-style-type: square; margin-top: 4px; }}
        li {{ margin-bottom: 5px; text-align: left; font-size: {base_font_size}; }}
        .section-header {{ text-transform: uppercase; font-weight: bold; border-bottom: 2px solid #333; padding-bottom: 4px; margin-bottom: 10px; margin-top: 18px; font-size: {section_font_size}; text-align: left; }}
        .content-box {{ margin-bottom: 15px; text-align: left; }}
        p {{ margin: 0; padding: 0; text-align: left; font-size: {base_font_size}; }}
    """

    color = t_config.get('color', '#1e3a8a')

    def render_row(left, right, bold=True):
        style = "font-weight:bold;" if bold else ""
        if for_pdf:
            return f'<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:2px; {style}"><tr><td align="left">{left}</td><td align="right">{right}</td></tr></table>'
        else:
            return f'<div style="display: flex; justify-content: space-between; {style} margin-bottom:3px;"><span>{left}</span> <span>{right}</span></div>'

    # Build internal section HTML
    sections_map = {}
    if summary:
        sections_map['summary'] = f"""
            <div class="content-box">
                <div class="section-header" style="border-color:{color}; color:{color};">{h_sum}</div>
                <div style="padding-left: 5px; font-size: {base_font_size}; line-height: 1.4;">{summary}</div>
            </div>"""
            
    if experience:
        exp_html = []
        for e in experience:
            if isinstance(e, dict):
                comp, role, date = e.get('company', ''), e.get('role', ''), e.get('date', '')
                bullets = "".join([f'<li style="margin-bottom: 3px;">{b}</li>' for b in e.get('bullets', [])])
                header = render_row(comp, date, bold=True)
                exp_html.append(f"""<div style="margin-bottom: 10px;">{header}<div style="font-style: italic; margin-bottom: 3px;">{role}</div><ul style="margin: 0; padding-left: 20px;">{bullets}</ul></div>""")
            else:
                exp_html.append(f'<li style="margin-bottom: 6px; padding-left: 5px;">{e}</li>')
        sections_map['experience'] = f"""<div class="content-box"><div class="section-header" style="border-color:{color}; color:{color};">{h_exp}</div>{"".join(exp_html) if (experience and isinstance(experience[0], dict)) else f'<ul style="margin-left: 0; padding-left: 18px;">{"".join(exp_html)}</ul>'}</div>"""
        
    if education:
        edu_html = []
        for ed in education:
            if isinstance(ed, dict):
                sch, deg, date = ed.get('school', ''), ed.get('degree', ''), ed.get('date', '')
                header = render_row(sch, date, bold=True)
                edu_html.append(f"""<div style="margin-bottom: 8px;">{header}<div style="font-style: italic;">{deg}</div></div>""")
            else:
                edu_html.append(f'<li style="margin-bottom: 4px; padding-left: 5px;">{ed}</li>')
        sections_map['education'] = f"""<div class="content-box"><div class="section-header" style="border-color:{color}; color:{color};">{h_edu}</div>{"".join(edu_html) if (education and isinstance(education[0], dict)) else f'<ul style="margin-left: 0; padding-left: 18px;">{"".join(edu_html)}</ul>'}</div>"""

    if skills:
        skill_tags = "".join([f'<span style="background:#f8fafc; padding:3px 8px; margin:2px; display:inline-block; border-radius:4px; font-size:9pt; color:#334155; border:1px solid #e2e8f0;">{s}</span>' for s in skills])
        if for_pdf: skill_tags = ", ".join(skills)
        sections_map['skills'] = f"""<div class="content-box"><div class="section-header" style="border-color:{color}; color:{color};">{h_skl}</div><p>{skill_tags}</p></div>"""

    for c_key, c_val in custom_sects.items():
        sections_map[c_key] = f"""<div class="content-box"><div class="section-header" style="border-color:{color}; color:{color};">{c_key}</div><div style="padding-left: 5px;">{c_val}</div></div>"""

    s_order = data.get('section_order', ['summary', 'experience', 'education', 'skills'])
    for core in ['summary', 'experience', 'education', 'skills']:
        if core not in s_order: s_order.append(core)
    
    sections_html = "".join([sections_map[sect] for sect in s_order if sect in sections_map])

    if template == "Executive Slate":
        style = common_style + f"""
            .sidebar {{ background-color: {color}; color: white; width: 30%; padding: 30px 15px; vertical-align: top; }}
            .main {{ width: 70%; padding: 35px 25px; vertical-align: top; }}
            h1.side-name {{ font-size: 16pt; color: white; margin-bottom: 25px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 15px; line-height:1.2; text-transform: uppercase; }}
        """
        photo_html = f'<div style="text-align:center;"><img src="{photo_url}" alt="" style="width:100px; height:100px; border-radius:50px; border:2px solid white; margin-bottom:20px;"></div>' if photo_url and needs_photo else ""
        content = f"""
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
                <td class="sidebar">
                    {photo_html}
                    <h1 class="side-name">{name}</h1>
                    <div style="padding: 0 5px;">
                        <h3 style="font-size: 10pt; color: #cbd5e1; margin-bottom: 10px; text-transform: uppercase;">{h_skl}</h3>
                        <p style="font-size: 9pt; color: #f1f5f9; line-height: 1.6;">{"<br>".join([f"• {s}" for s in skills])}</p>
                    </div>
                </td>
                <td class="main">{sections_html}</td>
            </tr>
        </table>
        """
    elif template == "Aura Elite":
        style = common_style + f"""
            .header {{ background-color: {color}; color: white; padding: 30px; text-align: center; }}
            .main {{ padding: 30px 40px; }}
        """
        photo_html = f'<div style="margin-bottom:15px;"><img src="{photo_url}" alt="" style="width:100px; height:100px; border-radius:50px; border:3px solid white; margin:0 auto;"></div>' if photo_url and needs_photo else ""
        content = f"""
        <div class="header">
            {photo_html}
            <h1 style="font-size: 24pt; margin: 0;">{name}</h1>
            <p style="opacity: 0.8; font-weight: bold; margin-top: 5px;">PROFESSIONAL EXCELLENCE</p>
        </div>
        <div class="main">
            {sections_html}
        </div>
        """
    elif template == "Spectrum Pro":
        style = common_style + f"""
            .sidebar {{ width: 33%; background: {color}; color: white; padding: 35px 20px; vertical-align: top; }}
            .main {{ width: 67%; padding: 35px; vertical-align: top; }}
        """
        photo_html = f'<div style="margin-bottom: 25px;"><img src="{photo_url}" alt="" style="width:100%; border-radius:10px; border:2px solid white;"></div>' if photo_url and needs_photo else ""
        content = f"""
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
                <td class="sidebar">
                    {photo_html}
                    <h1 style="font-size: 18pt; color: white; margin-bottom: 25px;">{name}</h1>
                    <h3 style="font-size: 10pt; color: rgba(255,255,255,0.7); text-transform: uppercase; margin-bottom: 15px;">{h_skl}</h3>
                    {"".join([f'<div style="font-size:9pt; margin-bottom:5px;">• {s}</div>' for s in skills])}
                </td>
                <td class="main">{sections_html}</td>
            </tr>
        </table>
        """
    elif template == "Harvard Classic" or template == "Standard Business":
        color = "#991b1b" if template == "Harvard Classic" else "#475569"
        style = common_style + f"""
            .page-padding {{ padding: 40px; }}
            h1.centered {{ text-align: center; font-size: 22pt; margin-bottom: 8px; color: {color}; text-transform: uppercase; }}
            .header-line {{ border-bottom: 2px solid {color}; margin-bottom: 20px; }}
        """
        content = f"""
        <div class="page-padding">
            <h1 class="centered">{name}</h1>
            <div class="header-line"></div>
            {sections_html}
        </div>
        """
    elif template == "ATS Titan":
        style = common_style + f"""
            .header {{ border-bottom: 3px solid #000; padding-bottom: 12px; margin-bottom: 20px; }}
            h1 {{ font-size: 22pt; text-transform: uppercase; }}
        """
        content = f"""
        <div style="padding:40px;">
            <div class="header"><h1>{name}</h1></div>
            {sections_html}
        </div>
        """
    elif template == "Global Specialist":
        style = common_style + f"""
            .sidebar {{ width: 28%; background: #f8fafc; padding: 30px 20px; vertical-align: top; border-right: 1px solid #ddd; }}
            .main {{ width: 72%; padding: 35px; vertical-align: top; }}
        """
        photo_html = f'<img src="{photo_url}" alt="" style="width:100%; border-radius:4px; margin-bottom:20px;">' if photo_url and needs_photo else ""
        content = f"""
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
                <td class="sidebar">
                    {photo_html}
                    <h3 style="color:{color}; font-size:11pt;">CONTACT</h3>
                    <p style="font-size:9pt; margin-bottom:20px;">{data.get('email', '')}</p>
                    <h3 style="color:{color}; font-size:11pt;">{h_skl}</h3>
                    {"".join([f'<div style="font-size:9pt; margin-bottom:4px;">{s}</div>' for s in skills])}
                </td>
                <td class="main">
                    <h1 style="color:{color}; font-size:24pt; margin:0;">{name}</h1>
                    <p style="color:#64748b; font-weight:bold; margin-bottom:25px;">PROFESSIONAL</p>
                    {sections_html}
                </td>
            </tr>
        </table>
        """
    else:
        # Visual Banner Fallback
        style = common_style + f"""
            .header-banner {{ background: {color}; color: white; padding: 30px; }}
            .main-content {{ padding: 30px 40px; }}
        """
        photo_html = f'<div style="float:right;"><img src="{photo_url}" alt="" style="width:90px; height:90px; border-radius:8px; border:2px solid white;"></div>' if photo_url and needs_photo else ""
        content = f"""
        <div class="header-banner">
            {photo_html}
            <h1 style="font-size: 22pt; margin:0;">{name}</h1>
            <p style="opacity: 0.9; font-weight: bold; margin-top:5px;">STRATEGIC PROFESSIONAL</p>
        </div>
        <div class="main-content">
            {sections_html}
        </div>
        """

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{style}</style></head>
    <body style="background: white;"><div style="{container_style}">{content}</div></body></html>"""
    
    if thumbnail:
        # Wrap for thumbnail preview inside frame
        return f"<!DOCTYPE html><html><head><meta charset='UTF-8'><style>{style}</style></head><body style='overflow:hidden; background:transparent;'><div style='{container_style}'>{content}</div></body></html>"
    return html

def convert_html_to_pdf(html_content: str) -> bytes:
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=result)
    return b"" if pisa_status.err else result.getvalue()
