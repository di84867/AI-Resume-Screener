
import streamlit as st

def render_workflow_module():
    st.markdown("## ⚡ Workflow Automation Matrix")
    st.markdown("IFTTT (If This Then That) logic for your hiring funnel.")

    if 'workflows' not in st.session_state:
        st.session_state.workflows = [
            {"trigger": "Score > 90%", "action": "Slack Alert in #hiring-managers", "active": True},
            {"trigger": "Status = Rejected", "action": "Email 'Polite Rejection' (Delay: 48h)", "active": True}
        ]

    # Create New Workflow
    with st.expander("➕ Create New Automation Rule"):
        c1, c2, c3 = st.columns([2, 0.5, 2])
        with c1:
            trigger = st.selectbox("IF Trigger", ["Candidate Score > 90%", "Candidate Score < 50%", "Application Stalled (7 days)"])
        with c2:
            st.markdown("<h3 style='text-align: center'>➜</h3>", unsafe_allow_html=True)
        with c3:
            action = st.selectbox("THEN Action", ["Send Calendly Link", "Send Rejection Email", "Slack Alert", "WhatsApp SMS"])
            
        if st.button("Activate Rule"):
            st.session_state.workflows.append({"trigger": trigger, "action": action, "active": True})
            st.success("Rule added to matrix.")

    # Active Workflows
    st.subheader("Active Matrix")
    for i, flow in enumerate(st.session_state.workflows):
        c1, c2, c3 = st.columns([3, 3, 1])
        c1.write(f"**IF** {flow['trigger']}")
        c2.write(f"**THEN** {flow['action']}")
        if c3.checkbox("Active", value=flow['active'], key=f"wf_{i}"):
            pass # Just UI toggle
            
    st.divider()
    st.subheader("🔌 Integrations status")
    st.success("✅ Slack Connected")
    st.success("✅ Gmail/Outlook Connected")
    st.warning("⚠️ Zoom Integration Disconnected")
