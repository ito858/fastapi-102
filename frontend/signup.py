# signup.py
import streamlit as st
import requests
from datetime import datetime  # Add this for date handling

BASE_URL = "http://127.0.0.1:8000"  # Matches backend /signup/ endpoint

def signup():
    st.subheader("Sign Up")

    # Username and Password (required)
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")

    # Membership Code (required)
    code = st.text_input("Membership Code", key="signup_code")

    # Personal Information
    with st.expander("Personal Information", expanded=True):
        nome = st.text_input("First Name (optional)", key="signup_nome")
        cognome = st.text_input("Last Name (optional)", key="signup_cognome")
#         nascita = st.text_input("Birth Date (optional, e.g., YYYY-MM-DD)", key="signup_nascita")
        nascita = st.date_input("Birth Date (optional)", value=None, min_value=datetime(1900, 1, 1), key="signup_nascita")
        sesso_options = {"Unspecified": 0, "Male": 1, "Female": 2}
        sesso = st.selectbox("Gender (optional)", options=list(sesso_options.keys()), key="signup_sesso")

    # Contact Information
    with st.expander("Contact Information", expanded=True):
        cellulare = st.text_input("Cell Phone", key="signup_cellulare")
        email = st.text_input("Email (optional)", key="signup_email")
        indirizzo = st.text_input("Address (optional)", key="signup_indirizzo")
        citta = st.text_input("City (optional)", key="signup_citta")
        cap = st.text_input("Postal Code (optional)", key="signup_cap")
        prov = st.text_input("Province (optional)", key="signup_prov")


    if st.button("Sign Up"):
        # Validate required fields
        required_fields = [username, password, cellulare, code]
        if not all(required_fields):
            st.error("Username, Password, Cell Phone, and Membership Code are required!")
            return

        # Prepare data for the backend
        signup_data = {
            "user": {"username": username, "password": password},
            "vip": {
                "cellulare": cellulare,
                "code": code,
                "Nome": nome,
                "cognome": cognome,
                "nascita": nascita.strftime("%Y-%m-%d") if nascita else None,  # Corrected typo: nascimento -> nascita
                "sesso": sesso_options[sesso],
                "Email": email,
                "Indirizzo": indirizzo,
                "Citta": citta,
                "Cap": cap,
                "Prov": prov
            }
        }

        try:
            response = requests.post(f"{BASE_URL}/signup/", json=signup_data)
            response.raise_for_status()
            st.success("Signup successful! Redirecting to login...")
            st.session_state.page = "Login"  # Set the page to Login
            st.rerun()  # Refresh the app to switch pages

        except requests.exceptions.RequestException as e:
            st.error(f"Signup failed: {e.response.json()['detail'] if e.response else 'Unknown error'} - Status: {response.status_code}")
