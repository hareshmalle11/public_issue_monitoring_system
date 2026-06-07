import streamlit as st
import requests
import textwrap

try:
    from frontend.config import API_URL
    from frontend.utils.api_client import parse_and_format_date, get_localities, upload_image
    from frontend.components.cards import render_complaint_card, render_ticket_tracker_details
except ModuleNotFoundError:
    from config import API_URL
    from utils.api_client import parse_and_format_date, get_localities, upload_image
    from components.cards import render_complaint_card, render_ticket_tracker_details

def show_citizen_portal():
    # If session state active tab is not in citizen options, default to Submit Grievance
    citizen_tabs = ["Submit Grievance", "My Complaints", "Track Ticket"]
    if st.session_state.active_tab not in citizen_tabs:
        st.session_state.active_tab = "Submit Grievance"

    user_id = st.session_state.user_data["user_id"]

    # 1. Submit Grievance
    if st.session_state.active_tab == "Submit Grievance":
        st.subheader("Register Civic Complaint")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            with st.form("grievance_form", clear_on_submit=True):
                complaint_desc = st.text_area(
                    "Complaint Description *",
                    placeholder="Provide a detailed description of the civic issue in about 30 t0 50 words (e.g format cause,impact,since when,urgency etc.)",
                    height=180
                )
                
                localities = get_localities()
                locality_input = st.selectbox("Locality *", options=localities)
                address_input = st.text_input("Detailed Address *", placeholder="House number, street name, block/area...")
                landmark_input = st.text_input("Landmark", placeholder="Near school, temple, main road...")
                uploaded_image = st.file_uploader("Upload Complaint Image (Optional)", type=["png", "jpg", "jpeg"])
                
                submit_complaint = st.form_submit_button("Submit Complaint to Municipal Office")
                
                if submit_complaint:
                    if len(complaint_desc.strip()) < 3 or not address_input.strip():
                        st.warning("Please provide a descriptive complaint text and address details.")
                    else:
                        image_url = None
                        if uploaded_image:
                            with st.spinner("Uploading evidence image..."):
                                image_url = upload_image(uploaded_image)
                        
                        payload = {
                            "complaint_text": complaint_desc,
                            "locality": locality_input,
                            "address": address_input,
                            "landmark": landmark_input if landmark_input else None,
                            "user_id": user_id,
                            "image_url": image_url
                        }
                        
                        with st.spinner("Routing complaint..."):
                            try:
                                res = requests.post(f"{API_URL}/api/complaints/", json=payload)
                                if res.status_code == 200:
                                    res_data = res.json()
                                    st.session_state.last_submission = res_data
                                    st.success("Civic complaint registered and routed successfully!")
                                else:
                                    st.error("Failed to route complaint.")
                            except Exception as e:
                                st.error(f"Connection error: {e}")
        
        with col2:
            if 'last_submission' in st.session_state:
                sub = st.session_state.last_submission
                g_info = sub["grievance"]
                pred = sub["prediction"]
                
                st.markdown(textwrap.dedent(f"""
                    <div class="custom-card">
                        <div class="card-title" style="color: #34d399;">✅ Grievance Registered</div>
                        <p style="margin: 0.25rem 0;"><b>Ticket Number:</b></p>
                        <code style="font-size: 1.15rem; color: #38bdf8; font-weight: 700;">{g_info.get('ticket_number')}</code>
                        
                        <hr style="margin: 1rem 0; border-color: rgba(255,255,255,0.05);"/>
                        
                        <p><b>Categorization:</b></p>
                        <span class="status-pill status-progress" style="font-size: 1rem; padding: 4px 16px;">{pred.get('category')}</span>
                        
                        <p style="margin-top: 1rem;"><b>Priority Assignment:</b></p>
                        <span class="priority-pill priority-{pred.get('priority').lower()}" style="font-size: 0.9rem; padding: 4px 12px; margin: 0;">{pred.get('priority')} Priority</span>
                        
                        <p style="margin-top: 1rem; color: #94a3b8; font-size: 0.85rem;">
                            The grievance has been sent to the <b>{g_info.get('locality')} Office</b> under the category <b>{pred.get('category')}</b>.
                        </p>
                    </div>
                """), unsafe_allow_html=True)
            else:
                st.markdown(textwrap.dedent("""
                    <div class="custom-card">
                        <div class="card-title">ℹ️ Submission Receipt</div>
                        <p style="color: #94a3b8;">Submit a complaint on the left to see the municipal classification routing response details in real time.</p>
                    </div>
                """), unsafe_allow_html=True)

    # 2. My Complaints
    elif st.session_state.active_tab == "My Complaints":
        st.subheader("My Grievance History")
        
        try:
            res = requests.get(f"{API_URL}/api/complaints/?user_id={user_id}")
            
            if res.status_code == 200:
                complaints = res.json()
                
                if not complaints:
                    st.info("You haven't submitted any complaints yet.")
                else:
                    # Filters
                    status_filter = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Resolved", "Rejected"])
                    
                    for c in complaints:
                        if status_filter != "All" and c.get("status") != status_filter:
                            continue
                            
                        submit_dt = parse_and_format_date(c.get("submission_date"), default_val="N/A")
                        res_dt = parse_and_format_date(c.get("resolved_date"), default_val=None)
                        
                        status_style = c.get("status").lower().replace(" ", "")
                        priority_style = c.get("priority").lower()
                        
                        # Solved indicator (tick mark if status is Resolved)
                        solved_mark = " ✔️" if c.get("status") == "Resolved" else ""
                        expander_label = f"🎫 Ticket: {c.get('ticket_number')} — Submitted: {submit_dt}{solved_mark}"
                        
                        with st.expander(expander_label):
                            # Render reusable card layout component
                            render_complaint_card(c, submit_dt, res_dt, priority_style, status_style)
                            
                            # Display complaint image if uploaded
                            if c.get("image_url"):
                                st.image(c.get("image_url"), caption="Citizen Uploaded Evidence", width=350)
                                
                            # Show Resolution Feedback System if complaint is Resolved
                            if c.get("status") == "Resolved":
                                st.write("### Rate Resolution & Feedback")
                                
                                # Check if feedback already submitted
                                fb_res = requests.get(f"{API_URL}/api/feedback/{c.get('grievance_id')}")
                                if fb_res.status_code == 200:
                                    fb_data = fb_res.json()
                                    st.success(f"Feedback submitted: Rating {'⭐'*fb_data.get('rating')}")
                                    if fb_data.get("feedback_text"):
                                        st.write(f"**Remarks**: {fb_data.get('feedback_text')}")
                                    if fb_data.get("image_url"):
                                        st.image(fb_data.get("image_url"), caption="Resolution Evidence Verification", width=300)
                                else:
                                    with st.form(f"feedback_form_{c.get('grievance_id')}"):
                                        rating_stars = st.radio(
                                            "Rate Resolution Quality",
                                            [5, 4, 3, 2, 1],
                                            format_func=lambda x: "⭐" * x,
                                            horizontal=True,
                                            key=f"star_fb_{c.get('grievance_id')}"
                                        )
                                        feedback_remarks = st.text_area("Feedback Text", placeholder="Write any comments on the resolution quality...")
                                        fb_img = st.file_uploader("Upload Resolution Verification Image (Optional)", type=["png", "jpg", "jpeg"], key=f"fb_img_{c.get('grievance_id')}")
                                        submit_fb = st.form_submit_button("Submit Resolution Feedback")
                                        
                                        if submit_fb:
                                            fb_img_url = None
                                            if fb_img:
                                                fb_img_url = upload_image(fb_img)
                                            fb_payload = {
                                                "grievance_id": c.get("grievance_id"),
                                                "user_id": user_id,
                                                "rating": rating_stars,
                                                "feedback_text": feedback_remarks if feedback_remarks else None,
                                                "image_url": fb_img_url
                                            }
                                            fb_post_res = requests.post(f"{API_URL}/api/feedback/", json=fb_payload)
                                            if fb_post_res.status_code == 200:
                                                st.success("Feedback submitted successfully!")
                                                st.rerun()
                                            else:
                                                st.error("Failed to save feedback.")
                                                
                            # Reopen Complaint Section
                            st.write("#### Reopen Complaint")
                            with st.form(f"reopen_form_{c.get('grievance_id')}"):
                                reopen_reason = st.text_area("Reason for Reopening", placeholder="Explain why you are reopening this complaint...")
                                submit_reopen = st.form_submit_button("Confirm Reopen Complaint")
                                
                                if submit_reopen:
                                    if not reopen_reason.strip():
                                        st.warning("Please specify a reason for reopening.")
                                    else:
                                        reopen_res = requests.post(
                                            f"{API_URL}/api/complaints/{c.get('grievance_id')}/reopen",
                                            json={"reason": reopen_reason}
                                        )
                                        if reopen_res.status_code == 200:
                                            st.success("Grievance has been reopened and set back to Pending.")
                                            st.rerun()
                                        else:
                                            st.error("Failed to reopen complaint.")
            else:
                st.error("Failed to load grievances.")
        except Exception as e:
            st.error(f"Connection error: {e}")

    # 3. Track Ticket
    elif st.session_state.active_tab == "Track Ticket":
        st.subheader("Direct Ticket Tracker")
        
        search_col1, search_col2 = st.columns([2, 1])
        
        with search_col1:
            ticket_number = st.text_input("Enter Ticket Number (e.g. PI-20260603-XXXXXX)").strip()
            track_btn = st.button("Query Progress", width="stretch", type="primary")
            
        with search_col2:
            st.markdown(textwrap.dedent("""
                <div style="padding: 1rem; background: rgba(255, 255, 255, 0.02); border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); font-size: 0.85rem; color: #94a3b8;">
                    Grievance status transitions are updated in real-time by reviewing department officers.
                </div>
            """), unsafe_allow_html=True)
            
        if track_btn or ticket_number:
            if not ticket_number:
                st.warning("Please type a valid ticket number.")
            else:
                try:
                    res = requests.get(f"{API_URL}/api/complaints/")
                    if res.status_code == 200:
                        all_complaints = res.json()
                        matched = [c for c in all_complaints if c.get("ticket_number") == ticket_number]
                        
                        if not matched:
                            st.warning(f"No grievance record found with ticket '{ticket_number}'.")
                        else:
                            c = matched[0]
                            submit_dt = parse_and_format_date(c.get("submission_date"), default_val="N/A")
                            res_dt = parse_and_format_date(c.get("resolved_date"), default_val="Awaiting resolution")
                            
                            status_style = c.get("status").lower().replace(" ", "")
                            priority_style = c.get("priority").lower()
                            
                            # Render tracker card details
                            render_ticket_tracker_details(c, submit_dt, res_dt, priority_style, status_style)
                            
                            if c.get("image_url"):
                                st.image(c.get("image_url"), caption="Citizen Evidence", width=400)
                    else:
                        st.error("Failed to look up ticket.")
                except Exception as e:
                    st.error(f"Error lookup: {e}")
