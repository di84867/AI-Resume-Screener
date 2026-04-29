import streamlit as st
import streamlit.components.v1 as components
import hashlib
import base64

def inject_security_css():
    """Injects high-end security CSS logic."""
    st.markdown("""
    <style>
        /* Security Overlay / Indicator (Optional subtle hint) */
        .security-locked {
            position: fixed;
            bottom: 10px;
            right: 10px;
            z-index: 9999;
            opacity: 0.3;
            pointer-events: none;
            font-size: 0.7rem;
            color: #2DD4BF;
        }
    </style>
    <div class="security-locked">🛡️ Shield Active</div>
    """, unsafe_allow_html=True)

def inject_defensive_js():
    """Injects obfuscated JS to prevent inspection and tampering."""
    # Obfuscated version of:
    # - Disable right click
    # - Disable F12, Ctrl+Shift+I, etc.
    # - Debugger trap
    defensive_js = """
    <script>
    (function(){
        const _0xS=["contextmenu","preventDefault","keydown","F12","ctrlKey","shiftKey","73","74","debugger","timeout"];
        
        // Disable Right Click
        document.addEventListener(_0xS[0], e => e[_0xS[1]]());

        // Disable DevTools Shortcuts
        document.addEventListener(_0xS[2], e => {
            if (e.key === _0xS[3] || (e[_0xS[4]] && e[_0xS[5]] && (e.keyCode == _0xS[6] || e.keyCode == _0xS[7]))) {
                e[_0xS[1]]();
            }
        });

        // Debugger Trap
        setInterval(function() {
            var s = performance.now();
            debugger;
            var e = performance.now();
            if (e - s > 100) {
                document.body.innerHTML = "<div style='height:100vh; display:flex; flex-direction:column; align-items:center; justify-content:center; background:#0f172a; color:#ef4444; font-family:sans-serif;'><h1>SECURITY BREACH</h1><p>Environment tampering detected. Visual interface terminated.</p><button onclick='location.reload()' style='padding:10px 20px; border-radius:8px; border:none; background:#2dd4bf; color:#0f172a; font-weight:bold; cursor:pointer;'>Restart Session</button></div>";
            }
        }, 1000);
    })();
    </script>
    """
    st.markdown(defensive_js, unsafe_allow_html=True)

def shadow_dom_wrap(content_id, title="Protected Layer"):
    """Creates a Shadow DOM container via JS injection."""
    shadow_script = f"""
    <div id="sd-host-{content_id}"></div>
    <script>
        (function() {{
            const h = document.getElementById('sd-host-{content_id}');
            if (h && !h.shadowRoot) {{
                const s = h.attachShadow({{mode: 'closed'}});
                const d = document.createElement('div');
                d.innerHTML = `<div style="padding:15px; border-radius:12px; background:rgba(45,212,191,0.05); border:1px solid rgba(45,212,191,0.2);">
                    <h5 style="margin:0 0 10px 0; color:#2DD4BF; font-family:sans-serif;">🔒 {title}</h5>
                    <div style="font-family:monospace; font-size:0.9rem; color:#94a3b8;">[Encapsulated Content - Restricted Access]</div>
                </div>`;
                s.appendChild(d);
            }}
        }})();
    </script>
    """
    return components.html(shadow_script, height=100)

def hash_secret(data):
    """Server-side hashing of sensitive data."""
    return hashlib.sha256(data.encode()).hexdigest()

def implement_all():
    """Main entry point to apply all security measures."""
    inject_security_css()
    inject_defensive_js()
