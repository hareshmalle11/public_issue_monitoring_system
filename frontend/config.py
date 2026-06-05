import os

import streamlit as st

DEFAULT_API_URL = "https://municipal-public-grievance-management.onrender.com"


def get_api_url() -> str:
    try:
        return st.secrets["API_URL"]
    except Exception:
        return os.getenv("API_URL", DEFAULT_API_URL)


# API Backend server connection
# For local-only backend testing, set API_URL=http://127.0.0.1:8000 in your environment.
API_URL = get_api_url()
