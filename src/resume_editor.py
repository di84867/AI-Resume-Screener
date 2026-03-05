
from typing import Dict, Any, List
import io
import json
import os
from xhtml2pdf import pisa

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
        "Silicon Vertex": {"desc": "Tech Geometric", "color": "#6366f1", "has_photo": False}
    }

def get_templates():
    """Load templates from registry or return defaults."""
    if os.path.exists(TEMPLATE_FILE):
        try:
            with open(TEMPLATE_FILE, 'r') as f:
                user_templates = json.load(f)
                # Merge with defaults, user templates can override or add
                defaults = get_default_templates()
                defaults.update(user_templates)
                return defaults
        except:
            return get_default_templates()
    return get_default_templates()

def save_user_template(name: str, config: Dict[str, Any]):
    """Save or update a template in the registry."""
    templates = get_templates()
    templates[name] = config
    
    # We only save the non-default ones to the JSON file to keep it clean
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
    common_tech_keywords = ["python", "java", "sql", "machine learning", "nlp", "aws", "docker", "kubernetes", "react"]
    for keyword in common_tech_keywords:
        if keyword in jd_lower and keyword not in resume_skills:
            suggestions['missing_skills'].append(keyword)
    return suggestions

def optimize_summary(data: Dict[str, Any]) -> str:
    skills = data.get('skills', [])
    top_skills = ", ".join(skills[:5]) if skills else "various technical"
    return f"Dynamic professional with specialized expertise in {top_skills}. Proven track record of delivering high-quality solutions."

def generate_html_resume(data: Dict[str, Any], template: str = "Executive Slate", for_pdf: bool = False) -> str:
    name = data.get('name', 'CANDIDATE NAME').upper()
    summary = data.get('summary', '')
    skills = data.get('skills', [])
    experience = data.get('experience', [])
    education = data.get('education', [])
    
    # Placeholder for photo if missing but template needs it
    templates = get_templates()
    t_config = templates.get(template, templates["Executive Slate"])
    needs_photo = t_config.get('has_photo', False)
    
    # Default placeholder image (Grey person icon)
    photo_url = data.get('photo', None)
    if needs_photo and not photo_url:
        photo_url = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

    # Dynamic Headings from Original Resume
    h = data.get('original_headings', {})
    h_sum = h.get('summary', 'Professional Summary')
    h_exp = h.get('experience', 'Professional Experience')
    h_edu = h.get('education', 'Academic Credentials')
    h_skl = h.get('skills', 'Technical Skills')

    page_css = "@page { size: a4; margin: 1cm; }" if for_pdf else ""
    container_style = "width: 100%;" if for_pdf else "width: 800px; margin: 0 auto; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1);"

    common_style = f"""
        {page_css}
        body {{ font-family: 'Helvetica', 'Arial', sans-serif; line-height: 1.5; color: #111; margin: 0; padding: 0; }}
        h1, h2, h3 {{ margin: 0; padding: 0; }}
        ul {{ padding-left: 20px; list-style-type: square; margin-top: 5px; }}
        li {{ margin-bottom: 6px; text-align: left; font-size: 10pt; }}
        .section-header {{ text-transform: uppercase; font-weight: bold; border-bottom: 2px solid #333; padding-bottom: 5px; margin-bottom: 12px; margin-top: 20px; font-size: 13pt; text-align: left; }}
        .content-box {{ margin-bottom: 20px; text-align: left; }}
        p {{ margin: 0; padding: 0; text-align: left; font-size: 10pt; }}
    """

    color = t_config.get('color', '#1e3a8a')

    # Content generation - DYNAMIC ORDERING
    s_order = data.get('section_order', ['summary', 'experience', 'education'])
    # Ensure all core sections are included even if not in order
    for core in ['summary', 'experience', 'education']:
        if core not in s_order: s_order.append(core)

    display_sections = []
    seen = set()
    
    for sect in s_order:
        if sect in seen: continue
        seen.add(sect)
        
        if sect == 'summary' and summary:
            display_sections.append(f"""
            <div class="content-box">
                <div class="section-header" style="border-color:{color}; color:{color};">{h_sum}</div>
                <div style="padding-left: 5px; font-size: 10pt; line-height: 1.6;">{summary}</div>
            </div>""")
        elif sect == 'experience' and experience:
            display_sections.append(f"""
            <div class="content-box">
                <div class="section-header" style="border-color:{color}; color:{color};">{h_exp}</div>
                <ul style="margin-left: 0; padding-left: 18px;">
                    {"".join([f'<li style="margin-bottom: 8px; padding-left: 5px;">{e}</li>' for e in experience])}
                </ul>
            </div>""")
        elif sect == 'education' and education:
            display_sections.append(f"""
            <div class="content-box">
                <div class="section-header" style="border-color:{color}; color:{color};">{h_edu}</div>
                <ul style="margin-left: 0; padding-left: 18px;">
                    {"".join([f'<li style="margin-bottom: 5px; padding-left: 5px;">{edu}</li>' for edu in education])}
                </ul>
            </div>""")

    sections_html = "".join(display_sections)


    if template == "Executive Slate":
        style = common_style + f"""
            .sidebar {{ background-color: {color}; color: white; width: 30%; padding: 30px 15px; vertical-align: top; }}
            .main {{ width: 70%; padding: 35px 25px; vertical-align: top; }}
            h1.side-name {{ font-size: 18pt; color: white; margin-bottom: 25px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 15px; line-height:1.2; }}
        """
        photo_html = f'<div style="text-align:center;"><img src="{photo_url}" style="width:110px; height:110px; border-radius:55px; border:3px solid white; margin-bottom:20px; object-fit: cover;"></div>' if photo_url else ""
        content = f"""
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
                <td class="sidebar">
                    {photo_html}
                    <h1 class="side-name">{name}</h1>
                    <div style="padding: 0 10px;">
                        <h3 style="font-size: 11pt; color: #cbd5e1; margin-bottom: 10px; text-transform: uppercase;">{h_skl}</h3>
                        <p style="font-size: 9pt; color: #f1f5f9; line-height: 1.8;">{"<br>".join([f"• {s}" for s in skills])}</p>
                    </div>
                </td>
                <td class="main">{sections_html}</td>
            </tr>
        </table>
        """
    elif template == "Aura Elite":
        style = common_style + f"""
            .header {{ background: linear-gradient(135deg, {color}, #1e3a8a); color: white; padding: 40px; text-align: center; border-radius: 0 0 50px 50px; position: relative; }}
            .main {{ padding: 40px 30px; }}
            .photo-frame {{ width: 120px; height: 120px; border-radius: 60px; border: 4px solid white; box-shadow: 0 10px 20px rgba(0,0,0,0.2); margin: 0 auto 20px auto; overflow: hidden; background: white; }}
        """
        photo_html = f'<div class="photo-frame"><img src="{photo_url}" style="width:100%; height:100%; object-fit: cover;"></div>' if photo_url else ""
        content = f"""
        <div class="header">
            {photo_html}
            <h1 style="font-size: 26pt; margin: 0; letter-spacing: -1px;">{name}</h1>
            <p style="opacity: 0.8; font-weight: bold; margin-top: 5px;">SENIOR STRATEGIC PROFESSIONAL</p>
        </div>
        <div class="main">
            {sections_html}
            <div class="content-box">
                <div class="section-header" style="border-color:{color}; color:{color};">{h_skl}</div>
                <p>{" ".join([f'<span style="background:#f1f5f9; padding:4px 10px; margin:3px; display:inline-block; border-radius:20px; font-size:9pt; color:{color}; font-weight:bold; border:1px solid {color}44;">{s}</span>' for s in skills])}</p>
            </div>
        </div>
        """
    elif template == "Spectrum Pro":
        style = common_style + f"""
            .sidebar {{ width: 35%; background: {color}; color: white; padding: 40px 20px; vertical-align: top; }}
            .main {{ width: 65%; padding: 40px; vertical-align: top; }}
            .skill-tag {{ display: block; background: rgba(255,255,255,0.1); padding: 8px 12px; margin-bottom: 5px; border-radius: 6px; font-size: 9pt; }}
        """
        photo_html = f'<div style="margin-bottom: 30px;"><img src="{photo_url}" style="width:100%; aspect-ratio:1/1; border-radius:15px; border:3px solid rgba(255,255,255,0.3); object-fit: cover;"></div>' if photo_url else ""
        content = f"""
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
                <td class="sidebar">
                    {photo_html}
                    <h1 style="font-size: 20pt; color: white; margin-bottom: 30px; line-height:1.1;">{name}</h1>
                    <h3 style="font-size: 10pt; color: rgba(255,255,255,0.7); text-transform: uppercase; margin-bottom: 15px;">{h_skl}</h3>
                    {" ".join([f'<div class="skill-tag">{s}</div>' for s in skills])}
                </td>
                <td class="main">{sections_html}</td>
            </tr>
        </table>
        """
    elif template == "Harvard Classic" or template == "Standard Business":
        color = "#991b1b" if template == "Harvard Classic" else "#475569"
        style = common_style + f"""
            .page-padding {{ padding: 35px; }}
            h1.centered {{ text-align: center; font-size: 24pt; margin-bottom: 10px; color: {color}; text-transform: uppercase; }}
            .header-line {{ border-bottom: 3px solid {color}; margin-bottom: 25px; }}
        """
        content = f"""
        <div class="page-padding">
            <h1 class="centered">{name}</h1>
            <div class="header-line"></div>
            {sections_html}
            <div class="content-box">
                <div class="section-header" style="border-color:{color}; color:{color};">{h_skl}</div>
                <p><b>{", ".join(skills)}</b></p>
            </div>
        </div>
        """
    elif template == "ATS Titan":
        style = common_style + f"""
            .header {{ border-bottom: 4px solid #000; padding-bottom: 15px; margin-bottom: 25px; }}
            h1 {{ font-size: 24pt; text-transform: uppercase; letter-spacing: 2px; }}
            .section-header {{ font-size: 11pt; border-bottom: 1px solid #000; margin-top: 15px; margin-bottom: 10px; font-weight: bold; }}
            li {{ margin-bottom: 3px; }}
        """
        content = f"""
        <div style="padding:40px;">
            <div class="header">
                <h1>{name}</h1>
                <p style="font-size:10pt; margin-top:5px;">{summary[:150]}...</p>
            </div>
            {sections_html}
            <div class="content-box">
                <div class="section-header">SKILLS</div>
                <p>{", ".join(skills)}</p>
            </div>
        </div>
        """
    elif template == "Quantum Chrono":
        style = common_style + f"""
            .timeline {{ border-left: 3px solid {color}; padding-left: 20px; margin-left: 10px; }}
            .header {{ background: {color}; color: white; padding: 25px; border-radius: 8px; margin-bottom: 30px; }}
        """
        content = f"""
        <div style="padding:30px;">
            <div class="header">
                <h1 style="margin:0; font-size:22pt;">{name}</h1>
            </div>
            <div class="timeline">
                {sections_html}
            </div>
            <div style="margin-top:20px; background:#f0fdf4; padding:15px; border-radius:8px;">
                <h3 style="color:{color}; margin-bottom:10px;">technical arsenal</h3>
                <p style="font-size:9pt;">{" • ".join(skills)}</p>
            </div>
        </div>
        """
    elif template == "Glacier Simple":
        style = common_style + f"""
            .header {{ border-top: 10px solid {color}; padding-top: 30px; margin-bottom: 40px; }}
            .section-header {{ color: {color} !important; border-bottom: none !important; margin-bottom: 5px !important; font-size: 14pt !important; }}
        """
        content = f"""
        <div style="padding:40px;">
            <div class="header">
                <h1 style="font-size:32pt; font-weight:300; color:{color};">{name}</h1>
            </div>
            <table width="100%">
                <tr>
                    <td width="65%" valign="top">
                        {sections_html}
                    </td>
                    <td width="35%" valign="top" style="padding-left:30px; border-left:1px solid #eee;">
                        <h3 style="color:{color}; margin-bottom:15px;">EXPERTISE</h3>
                        {"".join([f'<div style="margin-bottom:6px;">• {s}</div>' for s in skills])}
                    </td>
                </tr>
            </table>
        </div>
        """
    elif template == "Visionary Card":
        style = common_style + f"""
            .card {{ background: {color}; color: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 30px; }}
            .main {{ padding: 0 20px; }}
        """
        photo_html = f'<img src="{photo_url}" style="width:80px; height:80px; border-radius:50%; border:3px solid white; float:right;">' if photo_url else ""
        content = f"""
        <div style="padding:30px;">
            <div class="card">
                {photo_html}
                <h1 style="margin:0; font-size:26pt;">{name}</h1>
                <p style="opacity:0.9; margin-top:5px;">VISIONARY LEADER</p>
            </div>
            <div class="main">
                {sections_html}
                <div class="content-box">
                    <div class="section-header" style="color:{color}; border-color:{color};">{h_skl}</div>
                    <p>{"  //  ".join(skills)}</p>
                </div>
            </div>
        </div>
        """
    elif template == "Global Specialist":
        style = common_style + f"""
            .sidebar {{ width: 28%; background: #f8fafc; padding: 30px 20px; border-right: 2px solid {color}; }}
            .main {{ width: 72%; padding: 40px; }}
            h1 {{ color: {color}; font-size: 24pt; margin-bottom: 5px; }}
        """
        photo_html = f'<img src="{photo_url}" style="width:100%; border-radius:4px; margin-bottom:20px;">' if photo_url else ""
        content = f"""
        <table width="100%" cellspacing="0" cellpadding="0">
            <tr>
                <td class="sidebar" valign="top">
                    {photo_html}
                    <h3 style="color:{color}; margin-bottom:10px; font-size:11pt;">CONTACT</h3>
                    <p style="font-size:9pt; margin-bottom:20px;">{data.get('email', 'email@example.com')}</p>
                    
                    <h3 style="color:{color}; margin-bottom:10px; font-size:11pt;">SKILLS</h3>
                    {"".join([f'<div style="font-size:9pt; margin-bottom:4px; border-bottom:1px solid #e2e8f0; padding-bottom:2px;">{s}</div>' for s in skills])}
                </td>
                <td class="main" valign="top">
                    <h1 style="line-height:1;">{name}</h1>
                    <p style="color:#64748b; font-weight:bold; margin-bottom:25px;">SENIOR SPECIALIST</p>
                    {sections_html}
                </td>
            </tr>
        </table>
        """
    elif template == "Creative Grid":
        style = common_style + f"""
            .grid-container {{ display: table; width: 100%; border-spacing: 15px; }}
            .grid-item {{ display: table-cell; vertical-align: top; background: #fafafa; padding: 20px; border-radius: 10px; border: 1px solid #eee; }}
            .header-cell {{ background: {color}; color: white; border-radius: 10px; padding: 30px; margin-bottom: 20px; }}
        """
        photo_html = f'<img src="{photo_url}" style="width:100px; height:100px; border-radius:15px; border:3px solid white; float:left; margin-right:20px;">' if photo_url else ""
        content = f"""
        <div style="padding:20px;">
            <div style="background:{color}; color:white; padding:30px; border-radius:15px; margin-bottom:20px; display: table; width: 93%;">
                 <div style="display: table-cell; vertical-align: middle; width: 120px;">{photo_html}</div>
                 <div style="display: table-cell; vertical-align: middle;">
                    <h1 style="margin:0; font-size:28pt;">{name}</h1>
                    <p style="opacity:0.9;">CREATIVE PROFESSIONAL</p>
                 </div>
            </div>
            
            <div class="grid-container">
                <div class="grid-item" style="width: 40%; background: #fff0f5;">
                    <h3 style="color:{color}; border-bottom: 2px solid {color}; padding-bottom:5px;">SKILLS</h3>
                    <div style="margin-top:10px;">
                        {" ".join([f'<span style="background:{color}; color:white; padding:4px 8px; margin:2px; display:inline-block; border-radius:4px; font-size:8pt;">{s}</span>' for s in skills])}
                    </div>
                </div>
                <div class="grid-item" style="width: 60%;">
                    {sections_html}
                </div>
            </div>
        </div>
        """
    elif template == "Corporate Blue":
        style = common_style + f"""
            .header {{ background: {color}; height: 150px; position: relative; margin-bottom: 60px; }}
            .name-card {{ background: white; width: 80%; margin: 0 auto; box-shadow: 0 4px 10px rgba(0,0,0,0.1); padding: 30px; position: relative; top: 40px; text-align: center; border-radius: 4px; }}
            .content-pad {{ padding: 0 40px; }}
        """
        photo_html = f'<img src="{photo_url}" style="width:80px; height:80px; border-radius:50%; margin-bottom:10px;">' if photo_url else ""
        content = f"""
        <div>
            <div class="header">
                <div class="name-card">
                    {photo_html}
                    <h1 style="color:{color}; margin:0;">{name}</h1>
                    <p style="color:#64748b; font-size:10pt; font-weight:bold;">CORPORATE PROFESSIONAL</p>
                </div>
            </div>
            <div class="content-pad">
                {sections_html}
                <div style="border-top:1px solid #eee; padding-top:20px; margin-top:30px; text-align:center;">
                    <p style="font-weight:bold; color:{color};">CORE COMPETENCIES</p>
                    <p>{ " | ".join(skills) }</p>
                </div>
            </div>
        </div>
        """
    elif template == "Infographic Flow":
        style = common_style + f"""
            .flow-step {{ border-left: 4px solid {color}; padding-left: 20px; margin-bottom: 20px; margin-left: 20px; }}
            .circle {{ width: 12px; height: 12px; background: {color}; border-radius: 50%; position: absolute; left: 45px; margin-top: 6px; }}
        """
        photo_html = f'<img src="{photo_url}" style="width:120px; height:120px; border-radius:50%; border:5px solid {color}; margin:0 auto; display:block; margin-bottom:20px;">' if photo_url else ""
        content = f"""
        <div style="padding:40px;">
            {photo_html}
            <h1 style="text-align:center; color:{color}; font-size:28pt; margin-bottom:40px;">{name}</h1>
            
            <div style="background:#f8fafc; padding:20px; border-radius:10px; margin-bottom:30px;">
                <h3 style="color:{color}; border-bottom:1px solid {color}; padding-bottom:5px;">PROFESSIONAL JOURNEY</h3>
                {sections_html}
            </div>
            
            <div style="text-align:center;">
                <h3 style="color:{color};">SKILL SET</h3>
                {" ".join([f'<span style="border:1px solid {color}; color:{color}; padding:5px 10px; margin:5px; display:inline-block; border-radius:15px; font-weight:bold;">{s}</span>' for s in skills])}
            </div>
        </div>
        """

    elif template == "Nordic Clean":
        style = common_style + f"""
            .header {{ padding: 40px 0; border-bottom: 1px solid #eee; margin-bottom: 40px; text-align: center; }}
            .section-header {{ text-align: center; border-bottom: none; font-size: 10pt; letter-spacing: 2px; color: {color}; margin-bottom: 15px; }}
            p, li {{ text-align: center; list-style-position: inside; }}
            ul {{ padding: 0; }}
        """
        photo_html = f'<img src="{photo_url}" style="width:80px; height:80px; border-radius:50%; margin-bottom:15px; object-fit:cover;">' if photo_url else ""
        content = f"""
        <div style="padding: 0 60px;">
            <div class="header">
                {photo_html}
                <h1 style="font-weight: 300; font-size: 28pt; letter-spacing: 1px; margin-bottom: 10px;">{name}</h1>
                <p style="color: #94a3b8; font-size: 9pt; letter-spacing: 2px; text-transform: uppercase;">Professional Candidate</p>
                <p style="font-size: 9pt; margin-top: 10px;">{data.get('email', '')}</p>
            </div>
            
            <div class="content-box">
                <div class="section-header">PROFILE</div>
                <p style="max-width: 80%; margin: 0 auto; line-height: 1.8;">{summary}</p>
            </div>
            
            <div class="content-box">
                <div class="section-header">EXPERIENCE</div>
                {sections_html}
            </div>
            
            <div class="content-box" style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #fafafa;">
                <div class="section-header">EXPERTISE</div>
                <p style="color: {color};">{"  •  ".join(skills)}</p>
            </div>
        </div>
        """
    elif template == "Silicon Vertex":
        style = common_style + f"""
            .header {{ background: #0f172a; color: white; padding: 40px; clip-path: polygon(0 0, 100% 0, 100% 85%, 0 100%); margin-bottom: 30px; }}
            .section-header {{ color: {color}; border-left: 4px solid {color}; padding-left: 10px; border-bottom: none; }}
            .tech-pill {{ background: #f1f5f9; padding: 4px 10px; border-radius: 4px; display: inline-block; margin: 0 5px 5px 0; font-family: monospace; font-size: 9pt; }}
        """
        content = f"""
        <div>
            <div class="header">
                <h1 style="font-family: monospace; margin: 0; font-size: 32pt; color: {color};">&lt;{name} /&gt;</h1>
                <p style="opacity: 0.7; font-family: monospace; margin-top: 5px;">FULL STACK PROFESSIONAL</p>
            </div>
            
            <div style="padding: 0 40px;">
                <div class="content-box">
                    <div class="section-header">SYSTEM_LOG: EXPERIENCE</div>
                    {sections_html}
                </div>
                
                <div class="content-box">
                    <div class="section-header">KERNEL_MODULES: SKILLS</div>
                    <div style="margin-top: 10px;">
                    {"".join([f'<span class="tech-pill">{s}</span>' for s in skills])}
                    </div>
                </div>
            </div>
        </div>
        """
    else: 
        style = common_style + f"""
            .header-banner {{ background: {color}; color: white; padding: 35px 30px; text-align: left; }}
            .main-content {{ padding: 30px 30px; }}
        """
        photo_html = f'<div style="float: right;"> <img src="{photo_url}" style="width:105px; height:105px; border-radius:12px; border:3px solid white; object-fit: cover;"> </div>' if photo_url else ""
        content = f"""
        <div class="header-banner">
            {photo_html}
            <h1 style="font-size: 26pt; margin:0;">{name}</h1>
            <p style="opacity: 0.9; font-weight: bold; margin-top:5px;">STRATEGIC PROFESSIONAL</p>
        </div>
        <div class="main-content">
            {sections_html}
            <div class="content-box">
                <div class="section-header" style="border-color:{color}; color:{color};">{h_skl}</div>
                <p>{" ".join([f'<span style="background:#f1f5f9; border:1px solid #ddd; padding:3px 8px; margin:2px; display:inline-block; border-radius:4px; font-size:9pt;">{s}</span>' for s in skills])}</p>
            </div>
        </div>
        """

    return f"<html><head><meta charset='UTF-8'><style>{style}</style></head><body><div style='{container_style}'>{content}</div></body></html>"

def convert_html_to_pdf(html_content: str) -> bytes:
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=result)
    return b"" if pisa_status.err else result.getvalue()
