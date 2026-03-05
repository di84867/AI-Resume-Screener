
import json
import os
import pandas as pd
import streamlit as st
from datetime import datetime

TRACKER_FILE = "data/job_applications.json"

def load_applications():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(TRACKER_FILE):
        return []
    try:
        with open(TRACKER_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_application(company, role, status, date_applied, notes):
    apps = load_applications()
    apps.append({
        "id": len(apps) + 1,
        "company": company,
        "role": role,
        "status": status,
        "date": date_applied,
        "notes": notes
    })
    with open(TRACKER_FILE, 'w') as f:
        json.dump(apps, f, indent=4)

def update_application_status(app_id, new_status):
    apps = load_applications()
    for app in apps:
        if app["id"] == app_id:
            app["status"] = new_status
            break
    with open(TRACKER_FILE, 'w') as f:
        json.dump(apps, f, indent=4)

def delete_application(app_id):
    apps = load_applications()
    apps = [app for app in apps if app["id"] != app_id]
    with open(TRACKER_FILE, 'w') as f:
        json.dump(apps, f, indent=4)

def render_tracker_ui():
    st.markdown("## 📋 Job Application Tracker")
    st.caption("Plan, track, and manage your job search effectively.")

    with st.expander("➕ Add New Application", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1: co = st.text_input("Company Name")
        with c2: ro = st.text_input("Role Title")
        with c3: stt = st.selectbox("Status", ["Wishlist", "Applied", "Interview", "Offer", "Rejected"])
        nt = st.text_area("Notes / Next Steps")
        if st.button("Add Application", use_container_width=True):
            if co and ro:
                save_application(co, ro, stt, datetime.now().strftime("%Y-%m-%d"), nt)
                st.success("Added to tracker!")
                st.rerun()
            else:
                st.warning("Company and Role are required.")

    apps = load_applications()
    if not apps:
        st.info("No applications tracked yet. Add one above!")
    else:
        # Kanban Board View
        st.write("---")
        cols = st.columns(5)
        statuses = ["Wishlist", "Applied", "Interview", "Offer", "Rejected"]
        
        for i, status in enumerate(statuses):
            with cols[i]:
                st.markdown(f"**{status}**")
                for app in apps:
                    if app['status'] == status:
                        with st.container(border=True):
                            st.write(f"**{app['company']}**")
                            st.caption(app['role'])
                            st.caption(f"📅 {app['date']}")
                            
                            # Move Logic
                            c_move = st.popover("⋮")
                            with c_move:
                                new_st = st.selectbox("Move to:", statuses, key=f"move_{app['id']}")
                                if st.button("Update", key=f"btn_upd_{app['id']}"):
                                    update_application_status(app['id'], new_st)
                                    st.rerun()
                                if st.button("Delete", key=f"btn_del_{app['id']}", type="primary"):
                                    delete_application(app['id'])
                                    st.rerun()
