import streamlit as st
import pandas as pd
# Corrected import to use the new class name
from google_sheets_db import GoogleSheetsConnector
from admin_view import admin_main
from organizer_view import organizer_main
from user_view import user_main
from seminar_session import seminar_session_main

# --- Constants ---
USER_DATA_URL = "https://docs.google.com/spreadsheets/d/1nJq-DCS-bGMqtaVvU9VImWhOEet5uuL-uQHcMKBgSss/edit?usp=sharing"
USER_WORKSHEET_NAME = "Users"

# --- Page Configuration ---
st.set_page_config(
    page_title="PragyanAI Seminar Platform",
    page_icon="🎓",
    layout="wide"
)

# --- Main Application Logic ---
def main():
    """Main function to run the Streamlit app."""
    try:
        st.image("PragyanAI_Transperent.png", width=400)
    except Exception as e:
        st.warning(f"Logo not found. Please add 'PragyanAI_Transperent.png' to the root directory.")

    st.title("Guest Lecture and Seminar Platform")

    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_name = None

    # --- Initialize Google Sheets Connector ---
    # Using the correct, updated class name 'GoogleSheetsConnector'
    db_connector = GoogleSheetsConnector()
    user_sheet = db_connector.get_worksheet(USER_DATA_URL, USER_WORKSHEET_NAME)

    if user_sheet is None:
        # The connector already shows detailed errors, so a simple message here is fine.
        st.error("Could not establish a connection to the user database. The app cannot proceed.")
        return

    # --- Login/Signup/Main App View Logic ---
    if not st.session_state.logged_in:
        login_signup_forms(db_connector, user_sheet)
    else:
        menu(db_connector)

def login_signup_forms(db_connector, user_sheet):
    """Displays the login and signup forms in tabs."""
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        admin_login_form, user_login_form = st.columns(2)
        with admin_login_form:
            st.header("Admin Login")
            login_form(db_connector, user_sheet, role_check='Admin')
        with user_login_form:
            st.header("User / Organizer Login")
            login_form(db_connector, user_sheet, role_check=None)

    with signup_tab:
        st.header("Create a New Account")
        signup_form(db_connector, user_sheet)


def login_form(db_connector, user_sheet, role_check=None):
    """Creates a login form and handles authentication."""
    form_key = f"login_form_{role_check or 'user'}"
    with st.form(key=form_key):
        phone = st.text_input("Phone Number (Login ID)")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button(label="Login")

        if submit_button:
            if not phone or not password:
                st.warning("Please enter both phone number and password.")
                return

            users_df = db_connector.get_dataframe(user_sheet)
            required_columns = ['Phone(login)', 'Password', 'Status', 'Role', 'FullName']
            
            if users_df.empty:
                st.error("User database is currently empty.")
                return

            missing_columns = [col for col in required_columns if col not in users_df.columns]
            if missing_columns:
                st.error(f"The '{USER_WORKSHEET_NAME}' sheet is missing required columns: {', '.join(missing_columns)}.")
                return

            user_record = users_df[users_df['Phone(login)'].astype(str) == phone]

            if user_record.empty:
                st.error("User not found. Please check your phone number or sign up.")
            else:
                user_record = user_record.iloc[0]
                if user_record['Password'] == password:
                    if role_check and user_record['Role'] != role_check:
                        st.error(f"Access Denied. You do not have '{role_check}' permissions.")
                    elif user_record['Status'] == 'Approved':
                        st.session_state.logged_in = True
                        st.session_state.user_role = user_record['Role']
                        st.session_state.user_name = user_record['FullName']
                        st.rerun()
                    else:
                        st.warning("Your account is not yet approved by an admin.")
                else:
                    st.error("Incorrect password. Please try again.")

def signup_form(db_connector, user_sheet):
    """Creates a signup form and handles new user registration."""
    with st.form(key="signup_form"):
        st.subheader("Personal Information")
        full_name = st.text_input("Full Name *")
        email = st.text_input("Email *")
        phone_login = st.text_input("Phone (for login) *")
        phone_whatsapp = st.text_input("Phone (for WhatsApp)")

        st.subheader("Academic / Professional Information")
        college = st.text_input("College Name")
        branch = st.text_input("Branch / Specialization")
        reg_no = st.text_input("University Registration No.")
        pass_year = st.text_input("Year of Passing")
        experience = st.text_area("Experience (if any)")
        
        st.subheader("Presenter Profile (Optional)")
        brief_presenter = st.text_area("Brief Bio (if you plan to present)")
        linkedin = st.text_input("LinkedIn Profile URL")
        github = st.text_input("GitHub Profile URL")
        interest_area = st.text_area("Areas of Interest")

        st.subheader("Create Your Account")
        password = st.text_input("Password *", type="password")
        confirm_password = st.text_input("Confirm Password *", type="password")

        submit_button = st.form_submit_button("Sign Up")

        if submit_button:
            required_fields = [full_name, email, phone_login, password, confirm_password]
            if not all(required_fields):
                st.error("Please fill in all required fields marked with *.")
                return

            if password != confirm_password:
                st.error("Passwords do not match.")
                return
            
            users_df = db_connector.get_dataframe(user_sheet)
            if not users_df.empty and phone_login in users_df['Phone(login)'].astype(str).values:
                st.error("This phone number is already registered. Please log in.")
                return

            # This assumes the order of columns in your Google Sheet.
            # It's better to match headers, but append_row requires a list.
            new_user_data = [
                full_name, college, branch, reg_no, pass_year, phone_login,
                phone_whatsapp, email, password, "Not Approved", "Student",
                experience, brief_presenter, linkedin, github, interest_area
            ]
            
            if db_connector.append_record(user_sheet, new_user_data):
                st.success("Registration successful! An admin will approve your account shortly.")
            else:
                st.error("Failed to register user. Please try again later.")

def menu(db_connector):
    """Displays the sidebar menu based on user role."""
    st.sidebar.success(f"Welcome, {st.session_state.user_name}!")
    st.sidebar.write(f"Your Role: **{st.session_state.user_role}**")
    
    role = st.session_state.user_role
    page_options = {}

    if role == 'Admin':
        page_options = {
            "👑 Admin Dashboard": admin_main,
            "📝 Organizer Dashboard": organizer_main,
            "🏠 Home": user_main,
            "🎤 Live Session": seminar_session_main,
        }
    elif role in ['Organizer', 'Lead']:
        page_options = {
            "📝 Organizer Dashboard": organizer_main,
            "🏠 Home": user_main,
            "🎤 Live Session": seminar_session_main,
        }
    else: # Default for 'Student' or any other role
        page_options = {
            "🏠 Home": user_main,
            "🎤 Live Session": seminar_session_main,
        }

    selection = st.sidebar.radio("Go to", list(page_options.keys()))
    
    page_function = page_options[selection]
    # Pass the db_connector instance to the selected page's main function
    page_function(db_connector)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_name = None
        st.rerun()

# --- Entry point of the app ---
if __name__ == "__main__":
    main()
