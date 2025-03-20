import streamlit as st
import requests
from vip_dashboard import VIP, display_dashboard
import jwt  # Add this to decode the token manually for debugging

BASE_URL = "http://127.0.0.1:8000/api"

if "token" not in st.session_state:
    st.session_state.token = None

def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        try:
            response = requests.post(f"{BASE_URL}/login", data={"username": username, "password": password})
            response.raise_for_status()
            data = response.json()
            st.session_state.token = data["access_token"]
            st.success("Logged in successfully!")
            st.sidebar.write(f"Token: {st.session_state.token}")  # Show part of token
            # Decode token to show username (assuming JWT)
            try:
                decoded = jwt.decode(st.session_state.token, options={"verify_signature": False})
                st.sidebar.write(f"Username from token: {decoded.get('sub')}")
            except Exception as e:
                st.sidebar.error(f"Could not decode token: {e}")
        except requests.exceptions.RequestException as e:
            st.error(f"Login failed: {e.response.json()['detail'] if e.response else 'Unknown error'}")

def register():
    st.subheader("Register")
    username = st.text_input("Username", key="reg_username")
    password = st.text_input("Password", type="password", key="reg_password")
    if st.button("Register"):
        try:
            response = requests.post(f"{BASE_URL}/register", data={"username": username, "password": password})
            response.raise_for_status()
            st.success("Registered successfully! Please log in.")
        except requests.exceptions.RequestException as e:
            st.error(f"Registration failed: {e.response.json()['detail'] if e.response else 'Unknown error'}")

def dashboard():
    st.subheader("Dashboard")
    if st.session_state.token:
        try:
#             headers = {"Authorization": f"Bearer {st.session_state.token}"}
#             response = requests.get(f"{BASE_URL}/dashboard", headers=headers)
#             response.raise_for_status()
#             data = response.json()
#             st.write(f"Welcome, {data['username']}!")
#             st.write(data["message"])
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            st.write(f"Debug: Sending request to {BASE_URL}/api/dashboard")
            st.write(f"Debug: Sending request with token: {st.session_state.token}")
            response = requests.get(f"{BASE_URL}/dashboard", headers=headers)
            st.write(f"Debug: Response status code = {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                st.write(f"Welcome, {data['username']}!")
                st.write(f"Welcome, {data['username']}!")
                vip_data = data["vip"]
                # Convert hex string back to bytes for img if needed
                if vip_data["img"]:
                    vip_data["img"] = bytes.fromhex(vip_data["img"])
                vip = VIP(**vip_data)
                display_dashboard(vip)
            else:
                st.error(f"Failed to load dashboard: {response.json().get('detail', 'Unknown error')} - Status: {response.status_code}")
                st.write("Response content:", response.text)
                try:
                    decoded = jwt.decode(st.session_state.token, options={"verify_signature": False})
                    st.write(f"Debug: Decoded token payload: {decoded}")
                except JWTError as e:
                    st.write(f"Debug: Could not decode token: {e}")

            # Add logout button
            if st.button("Logout"):
                try:
                    # Call the logout endpoint
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    response = requests.post(f"{BASE_URL}/logout", headers=headers)
                    response.raise_for_status()
                    st.success("You have been logged out from all devices!")
                except requests.exceptions.RequestException as e:
                    st.error(f"Logout failed: {e.response.json()['detail'] if e.response else 'Unknown error'}")
                st.session_state.token = None
                st.rerun()  # Refresh the page
        except requests.exceptions.RequestException as e:
            st.error("Failed to load dashboard. Please log in again.")
            st.session_state.token = None
    else:
        st.warning("Please log in to access the dashboard.")


st.title("Membership System")
page = st.sidebar.selectbox("Choose a page", ["Login", "Register", "Dashboard"])

if page == "Login":
    login()
elif page == "Register":
    register()
elif page == "Dashboard":
    dashboard()
