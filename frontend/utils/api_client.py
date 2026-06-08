import streamlit as st
import requests
import pandas as pd
from config import API_URL

# Robust date parsing helper using pandas to support variable subsecond precision and timezones
def parse_and_format_date(dt_str, format_str="%B %d, %Y - %H:%M", default_val="N/A"):
    if not dt_str:
        return default_val
    try:
        dt = pd.to_datetime(dt_str)
        if pd.isna(dt):
            return default_val
        return dt.strftime(format_str)
    except Exception:
        return default_val

# Helper function to check connection to Backend
def test_backend_connection():
    try:
        response = requests.get(f"{API_URL}/")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

# Fetch localities dynamically from backend API
def get_localities():
    try:
        res = requests.get(f"{API_URL}/api/localities")
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return ["Madhapur", "Gachibowli", "Kukatpally", "Ameerpet", "Begumpet", "Jubilee Hills", "Miyapur", "Hitech City"]

# Helper to upload file to backend static storage fallback
def upload_image(image_file):
    try:
        files = {"file": (image_file.name, image_file.getvalue(), image_file.type)}
        res = requests.post(f"{API_URL}/api/complaints/upload", files=files)
        if res.status_code == 200:
            return res.json().get("image_url")
    except Exception as e:
        st.error(f"Error uploading image: {e}")
    return None
