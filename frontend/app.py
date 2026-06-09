from pathlib import Path
import sys

import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parent
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

import style
from config import API_URL
from utils.api_client import test_backend_connection
from views.auth import show_sidebar_info, show_auth_portal
from views.citizen import show_citizen_portal
from views.officer import show_officer_portal
from views.admin import show_officer_management

# Set page config for a premium wide layout
st.set_page_config(
    page_title="Municipal Public Grievance Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium CSS Injection for Dark Mode Aesthetics and custom UI elements
style.inject_custom_css()

# Initialize Session State variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_type" not in st.session_state:
    st.session_state.user_type = None  # "citizen" or "officer"
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Home"

# Sidebar Navigation Panel
is_connected = test_backend_connection()
show_sidebar_info()

# Rebranded Banners
st.markdown(
    """
<div class="header-banner">
    <h1>Municipal Public Grievance Management System</h1>
    <p>Submit, Track and Resolve Civic Issues Efficiently</p>
</div>
""",
    unsafe_allow_html=True,
)

# Connection alert if backend is offline
if not is_connected:
    st.error(
        f"System Offline: Cannot connect to Municipal Backend API at {API_URL}. "
        "Check that the Render backend is deployed and awake."
    )
    st.stop()

# Main Router
if not st.session_state.logged_in:
    show_auth_portal()
else:
    if st.session_state.user_type == "citizen":
        show_citizen_portal()
    elif st.session_state.user_type == "officer":
        if st.session_state.active_tab == "Officer Management":
            show_officer_management()
        else:
            show_officer_portal()
