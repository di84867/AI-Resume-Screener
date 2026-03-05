
import streamlit as st
import random

def render_rediscovery_module():
    st.markdown("## 🧠 Talent Rediscovery Engine")
    st.markdown("Don't pay for new ads. Your best candidate is likely already in your database.")

    st.subheader("🔍 Archive Deep Search")
    
    query = st.text_input("Search for skills, roles, or past notes (e.g., 'React Developer rejected last year')")
    
    if st.button("Search Archive"):
        st.write(f"Searching 14,205 archived profiles for '{query}'...")
        
        # Simulated Results
        results = [
            {"name": "Sarah Jenkins", "role": "Frontend Dev", "rejection_date": "6 months ago", "reason": "Salary Mismatch", "match": "94%"},
            {"name": "Mike Ross", "role": "React Intern", "rejection_date": "1 year ago", "reason": "Too Junior", "match": "88% - Now Senior"},
            {"name": "Jessica Pearson", "role": "UI Engineer", "rejection_date": "3 months ago", "reason": "Role Closed", "match": "82%"}
        ]
        
        for r in results:
            with st.expander(f"🥈 {r['name']} ({r['match']} Match)"):
                st.write(f"**Previous Role Applied:** {r['role']}")
                st.write(f"**Rejection Reason:** {r['reason']} ({r['rejection_date']})")
                st.warning("⚠️ This candidate uses technologies you need right now.")
                if st.button(f"Warm Up {r['name']}", key=r['name']):
                    st.success(f"Automated re-engagement sequence started for {r['name']}.")

    st.divider()
    
    st.subheader("🔥 'Warm Up' Automated Campaigns")
    st.info("Campaign 'Spring Hiring Blitz' is active. 450 past candidates contacted. 12% Open Rate.")
