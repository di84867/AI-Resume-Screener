
import streamlit as st
from datetime import datetime

# Simulated DB
if 'comments' not in st.session_state:
    st.session_state.comments = {} # {candidate_id: [comments]}

def render_workspace_module():
    st.markdown("## 🤝 Collaborative Hiring Workspace")
    st.markdown("Unify your hiring team with real-time scorecards and resume annotations.")

    if not st.session_state.processed_data:
        st.info("Upload resumes in the Dashboard to use this workspace.")
        return

    # Select Candidate
    candidates = list(st.session_state.processed_data.keys())
    selected = st.selectbox("Select Candidate to Review", candidates)
    
    if selected:
        c_data = st.session_state.processed_data[selected]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"📄 Resume: {c_data.get('name', selected)}")
            st.markdown(f"**Summary:** {c_data.get('summary', 'No summary available.')}")
            st.markdown("---")
            st.markdown(f"**Skills:** {', '.join(c_data.get('skills', []))}")
            
            # Annotation Simulation
            st.write("---")
            st.subheader("💬 Team Discussion")
            
            # Display existing comments
            if selected in st.session_state.comments:
                for comm in st.session_state.comments[selected]:
                    st.info(f"**{comm['user']}**: {comm['text']} ({comm['time']})")
            
            new_comment = st.text_input("Add a comment", key=f"comm_{selected}")
            if st.button("Post Comment"):
                if selected not in st.session_state.comments:
                    st.session_state.comments[selected] = []
                st.session_state.comments[selected].append({
                    "user": "You (HR Manager)",
                    "text": new_comment,
                    "time": datetime.now().strftime("%H:%M")
                })
                st.rerun()

        with col2:
            with st.container(border=True):
                st.subheader("📝 Digital Scorecard")
                
                tech_score = st.slider("Technical Proficiency", 0, 10, 7)
                culture_score = st.slider("Culture Fit", 0, 10, 5)
                comm_score = st.slider("Communication", 0, 10, 8)
                
                notes = st.text_area("Final Verdict Notes")
                
                final_score = (tech_score + culture_score + comm_score) / 3
                st.metric("Aggregate Score", f"{final_score:.1f}/10")
                
                if st.button("Submit Scorecard"):
                    st.success("Scorecard recorded on blockchain ledger.")
