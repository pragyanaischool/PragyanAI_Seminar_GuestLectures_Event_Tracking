import streamlit as st
import pandas as pd
from google_sheets_db import GoogleSheetsConnector
from admin_view import admin_main
from organizer_view import organizer_main
from user_view import user_main
from seminar_session import seminar_session_main

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
        st.session_state.user_phone = None

    # Connect to Google Sheets
    try:
        db_connector = GoogleSheetsConnector()
    except Exception as e:
        st.error(f"Failed to initialize the database connector. Please check your setup. Error: {e}")
        return

    # --- Login/Signup/Main App View Logic ---
    if not st.session_state.logged_in:
        login_signup_forms(db_connector)
    else:
        # Display the main application menu and content
        menu(db_connector)

def login_signup_forms(db_connector):
    """Displays the login and signup forms in tabs."""
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        admin_login_form, user_login_form = st.columns(2)
        with admin_login_form:
            st.header("Admin Login")
            login_form(db_connector, role_check='Admin')
        with user_login_form:
            st.header("User / Organizer Login")
            login_form(db_connector, role_check=None)

    with signup_tab:
        st.header("Create a New Account")
        signup_form(db_connector)


def login_form(db_connector, role_check=None):
    """Creates a login form and handles authentication."""
    USER_DATA_URL = "https://docs.google.com/spreadsheets/d/1nJq-DCS-bGMqtaVvU9VImWhOEet5uuL-uQHcMKBgSss/edit?usp=sharing"
    USER_WORKSHEET_NAME = "Users"
    
    with st.form(key=f"login_form_{role_check or 'user'}"):
        phone = st.text_input("Phone Number (Login ID)")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button(label="Login")

        if submit_button:
            if not phone or not password:
                st.warning("Please enter both phone number and password.")
                return

            user_sheet = db_connector.get_worksheet(USER_DATA_URL, USER_WORKSHEET_NAME)
            if not user_sheet:
                st.error("Could not connect to the user database. Please contact an admin.")
                return

            users_df = db_connector.get_dataframe(user_sheet)
            
            required_columns = ['Phone(login)', 'Password', 'Status', 'Role', 'FullName']
            if not all(col in users_df.columns for col in required_columns):
                st.error("User database is missing required columns. Please contact an admin.")
                return

            user_record = users_df[users_df['Phone(login)'].astype(str) == phone]

            if user_record.empty:
                st.error("User not found. Please check your phone number or sign up.")
            else:
                user_data = user_record.iloc[0]
                if user_data['Password'] == password:
                    if role_check and user_data['Role'] != role_check:
                        st.error(f"Access Denied. You do not have '{role_check}' permissions.")
                    elif user_data['Status'] == 'Approved':
                        st.session_state.logged_in = True
                        st.session_state.user_role = user_data['Role']
                        st.session_state.user_name = user_data['FullName']
                        st.session_state.user_phone = user_data['Phone(login)']
                        st.rerun()
                    else:
                        st.warning("Your account is not yet approved by an admin.")
                else:
                    st.error("Incorrect password. Please try again.")

def signup_form(db_connector):
    """Creates a signup form and handles new user registration."""
    USER_DATA_URL = "https://docs.google.com/spreadsheets/d/1nJq-DCS-bGMqtaVvU9VImWhOEet5uuL-uQHcMKBgSss/edit?usp=sharing"
    USER_WORKSHEET_NAME = "Users"

    with st.form(key="signup_form"):
        # Form fields...
        full_name = st.text_input("Full Name *")
        email = st.text_input("Email *")
        phone_login = st.text_input("Phone (for login) *")
        password = st.text_input("Password *", type="password")
        confirm_password = st.text_input("Confirm Password *", type="password")

        # Add other fields as needed
        
        submit_button = st.form_submit_button("Sign Up")

        if submit_button:
            if not all([full_name, email, phone_login, password, confirm_password]):
                st.error("Please fill in all required fields marked with *.")
                return
            if password != confirm_password:
                st.error("Passwords do not match.")
                return
            
            user_sheet = db_connector.get_worksheet(USER_DATA_URL, USER_WORKSHEET_NAME)
            if not user_sheet:
                 st.error("Could not connect to the user database for signup.")
                 return

            users_df = db_connector.get_dataframe(user_sheet)
            if not users_df.empty and phone_login in users_df['Phone(login)'].astype(str).values:
                st.error("This phone number is already registered. Please log in.")
                return

            new_user_data = {
                "FullName": full_name, "Email": email, "Phone(login)": phone_login,
                "Password": password, "Status": "Not Approved", "Role": "Student",
                # Add all other fields from your sheet here with empty strings as placeholders
                "CollegeName": "", "Branch": "", "RollNO(UniversityRegNo)": "", 
                "YearofPassing_Passed": "", "Phone(Whatsapp)": "", "Experience": "",
                "Brief_Presentor": "", "LinkedinProfile": "", "Github_Profile": "",
                "Area_of_Interest": "", "EnrolledSeminars": ""
            }
            
            # Ensure the order matches the Google Sheet columns
            column_order = [col for col in users_df.columns]
            new_row = [new_user_data.get(col, "") for col in column_order]

            if db_connector.add_record(user_sheet, new_row):
                st.success("Registration successful! An admin will approve your account shortly.")
            else:
                st.error("An error occurred during signup. Please try again.")

def menu(db_connector):
    """Displays the sidebar menu based on user role."""
    st.sidebar.success(f"Welcome, {st.session_state.user_name}!")
    st.sidebar.write(f"Your Role: **{st.session_state.user_role}**")
    
    page_options = {"🏠 Home": user_main, "🎤 Live Session": seminar_session_main}

    user_role = st.session_state.user_role
    if user_role == 'Admin':
        page_options["👑 Admin Dashboard"] = admin_main
    if user_role in ['Organizer', 'Lead']:
        page_options["📝 Organizer Dashboard"] = organizer_main

    selection = st.sidebar.radio("Go to", list(page_options.keys()))
    
    page_function = page_options[selection]
    page_function(db_connector)

    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Entry point of the app ---
if __name__ == "__main__":
    main()
