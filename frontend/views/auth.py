import streamlit as st
import requests
import textwrap

try:
    from frontend.config import API_URL
    from frontend.utils.api_client import get_localities
except ModuleNotFoundError:
    from config import API_URL
    from utils.api_client import get_localities

def handle_logout():
    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.session_state.user_data = None
    st.session_state.active_tab = "Home"
    st.rerun()

def show_sidebar_info():
    # Sidebar Navigation Panel
    st.sidebar.markdown(textwrap.dedent(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: #0ea5e9; margin: 0; font-weight: 700; letter-spacing: -0.5px;">🏛️ Civic Portal</h2>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.25rem;">Municipal Grievance System</p>
        </div>
        <hr style="margin: 0 0 1.5rem 0; border-color: rgba(255, 255, 255, 0.1);"/>
    """), unsafe_allow_html=True)

    if st.session_state.logged_in:
        u_data = st.session_state.user_data
        role_label = "Citizen" if st.session_state.user_type == "citizen" else "Municipal Officer"
        name_display = u_data.get("name") or u_data.get("officer_name") or u_data.get("username")
        
        st.sidebar.markdown(textwrap.dedent(f"""
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; border: 1px solid rgba(255,255,255,0.05);">
                <p style="color: #94a3b8; font-size: 0.8rem; margin: 0; text-transform: uppercase;">Authenticated As</p>
                <h4 style="color: #ffffff; margin: 0.25rem 0 0.5rem 0; font-weight: 600;">{name_display}</h4>
                <span class="status-pill status-progress" style="margin-bottom: 0.5rem;">{role_label}</span>
                {f'<div style="font-size: 0.8rem; color: #38bdf8; margin-top: 0.25rem;">📍 Locality: {u_data.get("locality")}</div>' if st.session_state.user_type == 'officer' else ''}
            </div>
        """), unsafe_allow_html=True)
        
        # Navigation mapping
        if st.session_state.user_type == "citizen":
            nav_options = ["Submit Grievance", "My Complaints", "Track Ticket"]
        else:
            nav_options = ["Locality Dashboard", "Manage Complaints", "Officer Management"]
            
        st.sidebar.subheader("Navigation")
        for opt in nav_options:
            if st.sidebar.button(opt, width="stretch", key=f"nav_{opt}"):
                st.session_state.active_tab = opt
                st.rerun()
                
        st.sidebar.markdown("<br/>", unsafe_allow_html=True)
        if st.sidebar.button("🔓 Sign Out", width="stretch", type="secondary"):
            handle_logout()
    else:
        if st.session_state.active_tab != "Home":
            st.session_state.active_tab = "Home"

def show_auth_portal():
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown(textwrap.dedent("""
            <div class="custom-card" style="height: 100%;">
                <div class="card-title">🏛️ Municipal Administration Portal</div>
                <p style="line-height: 1.6; color: #cbd5e1;">
                    Welcome to the official Municipal Public Grievance Management System. This portal provides a direct channel for citizens to report local infrastructure, electricity, sanitation, or public hazards, and allows localized municipal officers to manage and track resolution progress.
                </p>
                <h5 style="color: #ffffff; margin-top: 1.5rem;">System Capabilities:</h5>
                <div style="font-size: 1rem; color: #cbd5e1; line-height: 1.8; margin-top: 0.5rem;">
                    ✓ Complaint Registration<br/>
                    ✓ Complaint Categorization<br/>
                    ✓ Priority Identification<br/>
                    ✓ Locality-Based Monitoring<br/>
                    ✓ Real-Time Status Tracking<br/>
                    ✓ Citizen Feedback Management<br/>
                    ✓ Resolution Monitoring
                </div>
            </div>
        """), unsafe_allow_html=True)
        
    with col2:
        auth_mode = st.tabs(["🔑 Citizen Login", "📝 Citizen Register", "🛡️ Officer Login", "🛡️ Officer Register"])
        
        # 1. Citizen Login
        with auth_mode[0]:
            st.subheader("Citizen Login")
            with st.form("citizen_login_form"):
                email = st.text_input("Email Address")
                password = st.text_input("Password", type="password")
                submit_btn = st.form_submit_button("Sign In", width="stretch")
                
                if submit_btn:
                    if not email or not password:
                        st.warning("Please fill in all fields.")
                    else:
                        try:
                            res = requests.post(f"{API_URL}/api/auth/login", json={"email": email, "password": password})
                            if res.status_code == 200:
                                data = res.json()
                                st.session_state.logged_in = True
                                st.session_state.user_type = "citizen"
                                st.session_state.user_data = data["user"]
                                st.success("Logged in successfully!")
                                st.rerun()
                            else:
                                st.error(f"Login failed: {res.json().get('detail', 'Invalid credentials')}")
                        except Exception as e:
                            st.error(f"Error connecting: {e}")
                            
        # 2. Citizen Register
        with auth_mode[1]:
            st.subheader("Citizen Account Registration")
            with st.form("citizen_register_form"):
                reg_name = st.text_input("Full Name")
                reg_email = st.text_input("Email Address")
                reg_phone = st.text_input("Phone Number")
                reg_pass = st.text_input("Password (min. 6 characters)", type="password")
                reg_submit = st.form_submit_button("Register Citizen", width="stretch")
                
                if reg_submit:
                    if not reg_name or not reg_email or not reg_pass:
                        st.warning("Please fill in required fields (Name, Email, Password).")
                    else:
                        payload = {
                            "name": reg_name,
                            "email": reg_email,
                            "phone_number": reg_phone if reg_phone else None,
                            "password": reg_pass
                        }
                        try:
                            res = requests.post(f"{API_URL}/api/auth/register", json=payload)
                            if res.status_code == 200:
                                data = res.json()
                                st.session_state.logged_in = True
                                st.session_state.user_type = "citizen"
                                st.session_state.user_data = data["user"]
                                st.success("Citizen account created successfully!")
                                st.rerun()
                            else:
                                st.error(f"Registration failed: {res.json().get('detail', 'Could not register user')}")
                        except Exception as e:
                            st.error(f"Error connecting: {e}")
                            
        # 3. Officer Login
        with auth_mode[2]:
            st.subheader("Officer Login")
            with st.form("officer_login_form"):
                username = st.text_input("Username")
                off_password = st.text_input("Password", type="password")
                off_submit = st.form_submit_button("Sign In as Officer", width="stretch")
                
                if off_submit:
                    if not username or not off_password:
                        st.warning("Please fill in all fields.")
                    else:
                        try:
                            res = requests.post(
                                f"{API_URL}/api/auth/officer/login",
                                json={"username": username, "password": off_password}
                            )
                            if res.status_code == 200:
                                data = res.json()
                                officer_info = data["officer"]
                                
                                st.session_state.logged_in = True
                                st.session_state.user_type = "officer"
                                st.session_state.user_data = officer_info
                                
                                st.success(f"Officer login successful! Local Authority Assigned: {officer_info.get('locality')}")
                                st.rerun()
                            else:
                                st.error(f"Login failed: {res.json().get('detail', 'Invalid credentials')}")
                        except Exception as e:
                            st.error(f"Error connecting: {e}")
                            
        # 4. Officer Register (Gated with auth code 04032005)
        with auth_mode[3]:
            st.subheader("Register Officer Account")
            
            st.markdown(textwrap.dedent("""
                <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 0.75rem; border-radius: 4px; font-size: 0.85rem; color: #f87171; margin-bottom: 1rem;">
                    <b>Government Authorization Required</b><br/>
                    Only authorized municipal staff may create officer accounts.
                </div>
            """), unsafe_allow_html=True)
            
            auth_code = st.text_input("Enter Authorization Code", type="password", key="reg_gate_code")
            
            if auth_code:
                if auth_code != "04032005":
                    st.error("Government authorization required.")
                else:
                    st.success("Authorization Code Accepted. Please fill in the officer credentials:")
                    localities = get_localities()
                    
                    with st.form("officer_register_form"):
                        off_name = st.text_input("Officer Full Name")
                        off_username = st.text_input("Username")
                        off_email = st.text_input("Email Address")
                        off_reg_pass = st.text_input("Password (min. 6 characters)", type="password")
                        off_locality = st.selectbox("Assigned Locality Office", options=localities)
                        off_reg_submit = st.form_submit_button("Register Officer Account", width="stretch")
                        
                        if off_reg_submit:
                            if not off_name or not off_username or not off_email or not off_reg_pass:
                                st.warning("Please fill in username, email, and password.")
                            else:
                                payload = {
                                    "officer_name": off_name,
                                    "username": off_username,
                                    "email": off_email,
                                    "password": off_reg_pass,
                                    "locality": off_locality
                                }
                                try:
                                    reg_res = requests.post(f"{API_URL}/api/auth/officer/register", json=payload)
                                    if reg_res.status_code == 200:
                                        st.success("Officer registered successfully! Please log in above.")
                                    else:
                                        st.error(f"Registration failed: {reg_res.json().get('detail', 'Could not register officer')}")
                                except Exception as e:
                                    st.error(f"Error registering officer: {e}")
