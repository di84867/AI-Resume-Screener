
import streamlit as st
import pandas as pd
import plotly.express as px

def render_dei_module():
    st.markdown("## 🛡️ DEI & Compliance Guardian")
    st.markdown("Ensure fair hiring practices with AI-driven bias auditing.")

    tab1, tab2 = st.tabs(["⚖️ Bias Audit Logs", "🌍 Diversity Analytics"])

    with tab1:
        st.subheader("Explainable AI (XAI) Ranking Audit")
        st.write("Why was **Candidate A** ranked higher than **Candidate B**?")
        
        with st.container(border=True):
            st.markdown("#### Audit #39281 - Senior Developer Role")
            st.info("✅ **Passed**: No gendered language correlation found in scoring.")
            st.info("✅ **Passed**: University prestige bias check negative.")
            
            st.markdown("---")
            st.markdown("**Ranking Factors:**")
            st.progress(80, text="Skills Match (80%)")
            st.progress(15, text="Experience Duration (15%)")
            st.progress(5, text="Education (5%)")
            
            st.warning("⚠️ **Note:** 'Years of Experience' was highly weighted. Ensure this does not discriminate against younger talent.")

    with tab2:
        st.subheader("Pipeline Demographics (Anonymized)")
        
        # Fake Data for Charts
        df_gender = pd.DataFrame({'Gender': ['Male', 'Female', 'Non-Binary', 'Undisclosed'], 'Count': [45, 42, 5, 8]})
        fig1 = px.pie(df_gender, values='Count', names='Gender', title="Gender Distribution", hole=0.4)
        
        df_eth = pd.DataFrame({'Group': ['Group A', 'Group B', 'Group C', 'Group D'], 'Count': [30, 25, 20, 25]})
        fig2 = px.bar(df_eth, x='Group', y='Count', title="Diversity Groups (Anonymized)")
        
        c1, c2 = st.columns(2)
        c1.plotly_chart(fig1, use_container_width=True)
        c2.plotly_chart(fig2, use_container_width=True)
        
        st.success("🎉 You are meeting your diversity goals for Q3 2026.")
