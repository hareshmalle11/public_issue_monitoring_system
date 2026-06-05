import streamlit as st
import requests
import pandas as pd
import textwrap

try:
    from frontend.config import API_URL
    from frontend.utils.api_client import parse_and_format_date
    from frontend.components.cards import render_officer_complaint_card, render_dashboard_metrics
except ModuleNotFoundError:
    from config import API_URL
    from utils.api_client import parse_and_format_date
    from components.cards import render_officer_complaint_card, render_dashboard_metrics

def show_officer_portal():
    # If session state active tab is not in officer options, default to Locality Dashboard
    officer_tabs = ["Locality Dashboard", "Manage Complaints", "Officer Management"]
    if st.session_state.active_tab not in officer_tabs:
        st.session_state.active_tab = "Locality Dashboard"

    officer_locality = st.session_state.user_data["locality"]
    officer_id = st.session_state.user_data["officer_id"]

    # 1. Locality Dashboard Metrics & Charts
    if st.session_state.active_tab == "Locality Dashboard":
        st.subheader(f"Municipal Dashboard: {officer_locality} Locality")
        
        try:
            # Query backend metrics filtered specifically for officer locality
            summary_res = requests.get(f"{API_URL}/api/dashboard/summary?locality={officer_locality}")
            
            if summary_res.status_code == 200:
                summary = summary_res.json()
                
                # Render metrics UI component
                render_dashboard_metrics(summary)
                
                # Draw local graphs
                all_res = requests.get(f"{API_URL}/api/complaints?locality={officer_locality}")
                if all_res.status_code == 200:
                    df = pd.DataFrame(all_res.json())
                    
                    if not df.empty:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("#### Complaints by Category")
                            cat_counts = df["category"].value_counts()
                            st.bar_chart(cat_counts)
                        with col2:
                            st.write("#### Complaints Status Breakdown")
                            status_counts = df["status"].value_counts()
                            st.bar_chart(status_counts)
                    else:
                        st.info("No complaint charts available yet.")
            else:
                st.error("Failed to load dashboard metrics.")
        except Exception as e:
            st.error(f"Error loading dashboard: {e}")
            
    # 2. Manage Complaints (Locality-Based grouped by Category Expanders)
    elif st.session_state.active_tab == "Manage Complaints":
        st.subheader(f"Manage complaints for locality: {officer_locality}")
        
        try:
            # Fetch complaints belonging to officer locality
            res = requests.get(f"{API_URL}/api/complaints?locality={officer_locality}")
            if res.status_code == 200:
                complaints = res.json()
                
                # Priority sorting order helper: High Priority first!
                priority_order = {"High": 1, "Medium": 2, "Low": 3}
                
                # 1. Search Box
                search_query = st.text_input("🔍 Search Complaints (by Ticket, Description, Address, or Landmark)").strip().lower()
                
                # 2. Priority Filter Radio Bar
                st.write("**Priority Filter**")
                p_filter = st.radio(
                    "Select Priority Level to Display",
                    ["ALL", "HIGH", "MEDIUM", "LOW"],
                    horizontal=True
                )
                
                # Apply filters
                filtered_list = []
                for c in complaints:
                    # Search text filter
                    if search_query:
                        t_match = search_query in c.get("ticket_number", "").lower()
                        d_match = search_query in c.get("complaint_text", "").lower()
                        a_match = search_query in c.get("address", "").lower()
                        l_match = search_query in c.get("landmark", "").lower() if c.get("landmark") else False
                        if not (t_match or d_match or a_match or l_match):
                            continue
                            
                    # Priority filter
                    if p_filter != "ALL" and c.get("priority").upper() != p_filter:
                        continue
                        
                    filtered_list.append(c)
                
                # Group complaints by categories
                categories = ["Water", "Roads", "Electricity", "Traffic", "Drainage", "Sanitation", "Environment", "Public Property"]
                
                for cat in categories:
                    cat_complaints = [c for c in filtered_list if c.get("category") == cat]
                    
                    # Sort complaints by priority (High -> Medium -> Low)
                    sorted_complaints = sorted(
                        cat_complaints,
                        key=lambda x: priority_order.get(x.get("priority", "Low"), 3)
                    )
                    
                    expander_title = f"📂 {cat} ({len(sorted_complaints)} complaints)"
                    with st.expander(expander_title):
                        if not sorted_complaints:
                            st.write("No complaints in this category matching the filters.")
                        else:
                            for idx, c in enumerate(sorted_complaints):
                                priority_style = c.get("priority").lower()
                                status_style = c.get("status").lower().replace(" ", "")
                                submit_dt = parse_and_format_date(c.get("submission_date"), default_val="N/A")
                                res_dt = parse_and_format_date(c.get("resolved_date"), default_val=None)
                                
                                # Render officer complaint card layout component
                                render_officer_complaint_card(c, submit_dt, res_dt, priority_style, status_style)
                                
                                # Show image if present
                                if c.get("image_url"):
                                    st.image(c.get("image_url"), caption="Citizen Evidence Details", width=350)
                                    
                                # Fetch rating feedback details if Resolved
                                if c.get("status") == "Resolved":
                                    fb_res = requests.get(f"{API_URL}/api/feedback/{c.get('grievance_id')}")
                                    if fb_res.status_code == 200:
                                        fb = fb_res.json()
                                        st.markdown(f"**Citizen Rating**: {'⭐'*fb.get('rating')}")
                                        if fb.get('feedback_text'):
                                            st.write(f"**Citizen Remarks**: {fb.get('feedback_text')}")
                                        if fb.get('image_url'):
                                            st.image(fb.get('image_url'), caption="Citizen Feedback Evidence Verification", width=250)
                                
                                # Status Update Actions Panel
                                with st.form(key=f"status_form_{c.get('grievance_id')}_{idx}"):
                                    target_status = st.selectbox(
                                        "Select Resolution Status",
                                        ["Pending", "In Progress", "Resolved", "Rejected"],
                                        index=["Pending", "In Progress", "Resolved", "Rejected"].index(c.get("status"))
                                    )
                                    status_remarks = st.text_input("Officer Action Remarks", placeholder="Reason or updates on work status...")
                                    submit_status = st.form_submit_button("Submit Status Update")
                                    
                                    if submit_status:
                                        status_payload = {
                                            "status": target_status,
                                            "officer_id": officer_id,
                                            "remarks": status_remarks if status_remarks else f"Officer updated status to {target_status}"
                                        }
                                        try:
                                            status_patch_res = requests.patch(
                                                f"{API_URL}/api/complaints/{c.get('grievance_id')}/status",
                                                json=status_payload
                                            )
                                            if status_patch_res.status_code == 200:
                                                st.success("Complaint status updated!")
                                                st.rerun()
                                            else:
                                                st.error("Failed to update status.")
                                        except Exception as e:
                                            st.error(f"Error: {e}")
                                            
                                st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 1rem 0;'/>", unsafe_allow_html=True)
            else:
                st.error("Failed to load grievances queue.")
        except Exception as e:
            st.error(f"Error querying: {e}")
