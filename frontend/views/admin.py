import streamlit as st
import requests
import textwrap

try:
    from frontend.config import API_URL
    from frontend.utils.api_client import get_localities
except ModuleNotFoundError:
    from config import API_URL
    from utils.api_client import get_localities

def show_officer_management():
    st.subheader("Officer Account Management")
    
    st.markdown(textwrap.dedent("""
        <div style="background: rgba(14, 165, 233, 0.1); border-left: 4px solid #0ea5e9; padding: 0.75rem; border-radius: 4px; font-size: 0.85rem; color: #38bdf8; margin-bottom: 1rem;">
            <b>Administrative Access Portal</b><br/>
            Enter the government authorization key to unlock Create, Update, and Delete actions for officers.
        </div>
    """), unsafe_allow_html=True)
    
    admin_code = st.text_input("Enter Admin Authorization Code", type="password", key="admin_management_gate")
    
    if admin_code:
        if admin_code != "04032005":
            st.error("Authorization code is incorrect.")
        else:
            st.success("Access Unlocked. Choose administrative action:")
            
            admin_tabs = st.tabs(["➕ Create Officer", "📝 Update Officer", "❌ Delete Officer"])
            localities = get_localities()
            
            # Tab 1: Create Officer
            with admin_tabs[0]:
                st.write("### Create Officer Account")
                with st.form("admin_create_officer_form"):
                    c_name = st.text_input("Officer Full Name")
                    c_user = st.text_input("Username")
                    c_email = st.text_input("Email Address")
                    c_pass = st.text_input("Password (min. 6 characters)", type="password")
                    c_locality = st.selectbox("Assigned Locality", options=localities)
                    c_submit = st.form_submit_button("Submit & Save Officer")
                    
                    if c_submit:
                        if not c_name or not c_user or not c_email or not c_pass:
                            st.warning("Please fill in all details.")
                        else:
                            c_payload = {
                                "officer_name": c_name,
                                "username": c_user,
                                "email": c_email,
                                "password": c_pass,
                                "locality": c_locality
                            }
                            try:
                                c_res = requests.post(f"{API_URL}/api/officers", json=c_payload)
                                if c_res.status_code == 200:
                                    st.success(f"Officer '{c_user}' created successfully!")
                                else:
                                    st.error(f"Failed to create: {c_res.json().get('detail')}")
                            except Exception as e:
                                st.error(f"Error: {e}")
                                
            # Tab 2: Update Officer
            with admin_tabs[1]:
                st.write("### Update Officer Account")
                
                try:
                    off_res = requests.get(f"{API_URL}/api/officers")
                    if off_res.status_code == 200:
                        officers_list = off_res.json()
                    else:
                        officers_list = []
                except Exception:
                    officers_list = []
                    
                if not officers_list:
                    st.info("No officers accounts found to update.")
                else:
                    off_options = {
                        f"{o.get('officer_name')} (@{o.get('username')}) - {o.get('locality')}": o
                        for o in officers_list
                    }
                    selected_key = st.selectbox("Select Officer to Edit", options=list(off_options.keys()))
                    selected_officer = off_options[selected_key]
                    
                    with st.form("admin_update_officer_form"):
                        u_user = st.text_input("Change Username", value=selected_officer.get("username"))
                        u_pass = st.text_input("Change Password (leave blank to keep unchanged)", type="password")
                        u_locality = st.selectbox(
                            "Change Assigned Locality",
                            options=localities,
                            index=localities.index(selected_officer.get("locality")) if selected_officer.get("locality") in localities else 0
                        )
                        u_submit = st.form_submit_button("Apply Modifications")
                        
                        if u_submit:
                            u_payload = {
                                "username": u_user if u_user != selected_officer.get("username") else None,
                                "password": u_pass if u_pass.strip() else None,
                                "locality": u_locality if u_locality != selected_officer.get("locality") else None
                            }
                            # Remove None values
                            u_payload = {k: v for k, v in u_payload.items() if v is not None}
                            
                            if not u_payload:
                                st.warning("No edits were made to default values.")
                            else:
                                try:
                                    patch_res = requests.patch(
                                        f"{API_URL}/api/officers/{selected_officer.get('officer_id')}",
                                        json=u_payload
                                    )
                                    if patch_res.status_code == 200:
                                        st.success("Officer account modified successfully!")
                                    else:
                                        st.error("Failed to edit account.")
                                except Exception as e:
                                    st.error(f"Error: {e}")
                                    
            # Tab 3: Delete Officer
            with admin_tabs[2]:
                st.write("### Remove Officer Account")
                
                try:
                    off_res = requests.get(f"{API_URL}/api/officers")
                    officers_list = off_res.json() if off_res.status_code == 200 else []
                except Exception:
                    officers_list = []
                    
                if not officers_list:
                    st.info("No officers accounts found to remove.")
                else:
                    del_options = {
                        f"{o.get('officer_name')} (@{o.get('username')}) - {o.get('locality')}": o
                        for o in officers_list
                    }
                    del_key = st.selectbox("Select Officer to Delete", options=list(del_options.keys()))
                    del_officer = del_options[del_key]
                    
                    with st.form("admin_delete_officer_form"):
                        st.warning(f"Warning: You are about to permanently delete the officer account for '{del_officer.get('officer_name')}' (@{del_officer.get('username')}). This cannot be undone.")
                        confirm_del = st.checkbox("I confirm I want to permanently delete this officer account")
                        del_submit = st.form_submit_button("Remove Account Permanent")
                        
                        if del_submit:
                            if not confirm_del:
                                st.warning("Please tick the confirmation checkbox to authorize deletion.")
                            else:
                                try:
                                    del_res = requests.delete(f"{API_URL}/api/officers/{del_officer.get('officer_id')}")
                                    if del_res.status_code == 200:
                                        st.success("Officer account removed successfully.")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete account.")
                                except Exception as e:
                                    st.error(f"Error: {e}")
