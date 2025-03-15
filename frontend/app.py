import streamlit as st
import requests

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
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            response = requests.get(f"{BASE_URL}/dashboard", headers=headers)
            response.raise_for_status()
            data = response.json()
            st.write(f"Welcome, {data['username']}!")
            st.write(data["message"])

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
