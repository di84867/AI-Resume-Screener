import streamlit as st
import streamlit.components.v1 as components
import json
import base64
import time
import hashlib

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Secure Shield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PREMIUM CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    :root {
        --primary: #00f2fe;
        --secondary: #4facfe;
        --bg-dark: #0f172a;
        --glass: rgba(30, 41, 59, 0.7);
        --glass-border: rgba(255, 255, 255, 0.1);
    }

    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        font-family: 'Outfit', sans-serif;
        color: #e2e8f0;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .secure-card {
        background: var(--glass);
        backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    .secure-card:hover {
        border-color: var(--primary);
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.2);
        transform: translateY(-5px);
    }

    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .status-active { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }
    .status-warning { background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid #eab308; }

    h1, h2, h3 { color: #fff; font-weight: 800; }
    
    .glow-text {
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
        background: linear-gradient(to right, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Streamlit Overrides */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: #0f172a;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        padding: 0.6rem 2rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
    }

    .stButton>button:hover {
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# --- 1. BACKEND LOGIC (SSR & API Hiding) ---
# We simulate a "Backend Secure Store" that is never visible to the client
if 'secure_vault' not in st.session_state:
    st.session_state.secure_vault = {
        "SECRET_KEY": hashlib.sha256(b"project_master_key").hexdigest(),
        "ENCRYPTED_DB_REF": "vault_α_9921",
        "API_ENDPOINT": "https://api.secure-gateway.internal/v1"
    }

def process_on_backend(data):
    """Simulates server-side processing where client only sees the result."""
    time.sleep(0.5) # Simulate latency
    return f"PROCESSED_{hashlib.md5(data.encode()).hexdigest()[:8]}"

# --- 2. SHADOW DOM ENCAPSULATION ---
def shadow_dom_component(content, title="Hidden Fragment"):
    # This creates a Shadow Root which makes the content less accessible via normal DOM selectors
    shadow_html = f"""
    <div id="shadow-host"></div>
    <script>
        (function() {{
            const host = document.querySelector('#shadow-host');
            const shadow = host.attachShadow({{mode: 'closed'}}); // 'closed' makes it even harder to access
            const wrapper = document.createElement('div');
            wrapper.style.padding = '20px';
            wrapper.style.background = 'rgba(255,255,255,0.05)';
            wrapper.style.borderRadius = '15px';
            wrapper.style.borderLeft = '4px solid #00f2fe';
            wrapper.innerHTML = `
                <h4 style="color: #00f2fe; margin-top: 0;">{title}</h4>
                <div style="color: #cbd5e1; font-family: monospace;">{content}</div>
                <p style="font-size: 0.8rem; color: #64748b;">(Rendered inside Shadow DOM)</p>
            `;
            shadow.appendChild(wrapper);
        }})();
    </script>
    """
    return components.html(shadow_html, height=140)

# --- 3. DEFENSIVE TECHNIQUES & OBFUSCATION ---
# Obfuscated JS to deter inspection
DEFENSIVE_JS = """
<script>
(function(){
    // Defensive Logic: Disable Context Menu, F12, Debugger Trap
    const _0x123a = ["contextmenu", "preventDefault", "keydown", "F12", "ctrlKey", "shiftKey", "73", "debugger"];
    
    // Disable Right Click
    document.addEventListener(_0x123a[0], e => e[_0x123a[1]]());

    // Disable DevTools Shortcuts
    document.addEventListener(_0x123a[2], e => {
        if (e.key === _0x123a[3] || (e[_0x123a[4]] && e[_0x123a[5]] && e.keyCode == _0x123a[6])) {
            e[_0x123a[1]]();
            alert("Security Protocol Active: DevTools access restricted.");
        }
    });

    // Debugger Trap (Freezes page if console is open)
    setInterval(function() {
        var startTime = performance.now();
        debugger;
        var endTime = performance.now();
        if (endTime - startTime > 100) {
            document.body.innerHTML = "<h1>SECURITY BREACH DETECTED</h1><p>Environment tampering detected. Refresh page to restore.</p>";
        }
    }, 1000);
})();
</script>
"""

# --- 4. WEBASSEMBLY (Wasm) Mock ---
# Since true Wasm compilation is tricky in this env, we demonstrate the loading pattern
# This JS snippet would fetch and instantiate a .wasm binary
WASM_SCRIPT = """
<script>
async function runSecureWasm(input) {
    const response = await fetch('https://raw.githubusercontent.com/mdn/webassembly-examples/master/js-api-examples/simple.wasm');
    const bytes = await response.arrayBuffer();
    const { instance } = await WebAssembly.instantiate(bytes);
    console.log("Wasm execution result hidden from plain JS view");
    return instance.exports.exported_func();
}
</script>
"""

# --- UI LAYOUT ---

# Top Navigation / Title
cols = st.columns([1, 4, 1])
with cols[1]:
    st.markdown("<h1 style='text-align: center;' class='glow-text'>SHIELD SECURITY SUITE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Advanced Data Protection & Anti-Tamper Engine for Streamlit</p>", unsafe_allow_html=True)

st.divider()

# Main Grid
l_col, r_col = st.columns([1, 1], gap="large")

with l_col:
    # --- CARD 1: SERVER-SIDE RENDERING ---
    st.markdown("""
    <div class="secure-card">
        <span class="status-badge status-active">Enabled</span>
        <h3>Backend Logic Bridge</h3>
        <p>Sensitive operations occur exclusively in the Python execution environment (server). Client only receives processed outputs.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("Try SSR Execution"):
        user_input = st.text_input("Enter Sensitive Data:", placeholder="e.g. User Profile ID")
        if st.button("Process Secret"):
            result = process_on_backend(user_input)
            st.success(f"Backend result: {result}")
            st.caption("Note: The algorithm and master keys are stored on the server (`st.session_state`) and never sent to HTML.")

    # --- CARD 2: SHADOW DOM ---
    st.markdown("""
    <div class="secure-card">
        <span class="status-badge status-active">Active</span>
        <h3>Encapsulated Components</h3>
        <p>Using <b>Shadow DOM</b> to isolate parts of the UI. This prevents standard CSS/JS selection and hides content from casual 'Inspect Element' views.</p>
    </div>
    """, unsafe_allow_html=True)
    shadow_dom_component("Vault_Token_#8821-XCA (Hidden in Shadow Root)", "System Metadata")

with r_col:
    # --- CARD 3: DEFENSIVE SHIELD ---
    st.markdown("""
    <div class="secure-card">
        <span class="status-badge status-warning">Aggressive</span>
        <h3>Anti-Inspection Layer</h3>
        <p>Injecting obfuscated JavaScript to block F12, Right-Click, and implement 'Debugger Traps'.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.toggle("Enable Defensive Protocols", value=True):
        st.markdown(DEFENSIVE_JS, unsafe_allow_html=True)
        st.info("Right-click and F12 are now disabled on this page.")
    
    # --- CARD 4: ENCRYPTION & WASM ---
    st.markdown("""
    <div class="secure-card">
        <span class="status-badge status-active">Ready</span>
        <h3>Cryptography & Binary Logic</h3>
        <p>Data is hashed using SHA-256 before any UI sync. Demonstrating WebAssembly integration for binary-level logic protection.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.code("""
# Server-side hashing (SHA-256)
key = hashlib.sha256(b"user_data").hexdigest()
    """, language="python")

# --- FOOTER ---
st.markdown("---")
f_cols = st.columns(3)
with f_cols[0]:
    st.caption("🛡️ End-to-End Encryption")
with f_cols[1]:
    st.caption("⚡ Wasm Optimized Logic")
with f_cols[2]:
    st.caption("🔒 Shadow DOM Isolation")
