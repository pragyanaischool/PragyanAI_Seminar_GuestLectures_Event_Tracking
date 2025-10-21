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
    # Display logo in a centered column
    col1, col2, col3 = st.columns([1, 2, 1]) # Adjusted columns for better centering
    with col2:
        try:
            # use_column_width=True makes the image responsive to the column width
            st.image("PragyanAI_Transperent.png", use_container_width=True)
        except Exception as e:
            st.warning(f"Logo not found. Please add 'PragyanAI_Transperent.png' to the root directory.")

    st.title("Guest Lecture and Seminar Platform")

    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_name = None
        st.session_state.selected_seminar_title = None # Initialize selected seminar

    # Connect to Google Sheets
    try:
        db_connector = GoogleSheetsConnector()
    except Exception as e:
        st.error(f"Failed to initialize the database connector. Please check your secrets. Error: {e}")
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

    # Define constants for sheet URL and worksheet names
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1nJq-DCS-bGMqtaVvU9VImWhOEet5uuL-uQHcMKBgSss/edit?usp=sharing"
    USER_WORKSHEET_NAME = "Users"
    ADMIN_WORKSHEET_NAME = "Admins" # New worksheet for Admins

    with login_tab:
        admin_login_form, user_login_form = st.columns(2)
        with admin_login_form:
            st.header("Admin Login")
            # Point Admin login to the "Admins" sheet
            login_form(db_connector, SHEET_URL, ADMIN_WORKSHEET_NAME, role_check='Admin')
        with user_login_form:
            st.header("User / Organizer Login")
            # Point User login to the "Users" sheet
            login_form(db_connector, SHEET_URL, USER_WORKSHEET_NAME, role_check=None)

    with signup_tab:
        st.header("Create a New Account")
        # Signups should always go to the "Users" sheet
        signup_form(db_connector, SHEET_URL, USER_WORKSHEET_NAME)


def login_form(db_connector, sheet_url, worksheet_name, role_check=None):
    """Creates a login form and handles authentication."""
    with st.form(key=f"login_form_{worksheet_name}"):
        phone = st.text_input("Phone Number (Login ID)")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button(label="Login")

        if submit_button:
            if not phone or not password:
                st.warning("Please enter both phone number and password.")
                return

            try:
                user_sheet = db_connector.get_worksheet(sheet_url, worksheet_name)
                if not user_sheet:
                    st.error(f"Failed to connect to the '{worksheet_name}' database. Please check the sheet URL and worksheet name.")
                    return

                users_df = db_connector.get_dataframe(user_sheet)
                required_columns = ['Phone(login)', 'Password', 'Status', 'Role', 'FullName']
                if not all(col in users_df.columns for col in required_columns):
                    st.error(f"The '{worksheet_name}' sheet is missing one or more required columns. Please ensure it has: {', '.join(required_columns)}.")
                    return

                if users_df.empty:
                    st.error(f"The '{worksheet_name}' database is currently empty.")
                    return

                # Strip whitespace from both input and sheet data for a robust comparison
                user_record = users_df[users_df['Phone(login)'].astype(str).str.strip() == phone.strip()]

                if user_record.empty:
                    st.error("User not found. Please check your phone number or sign up.")
                else:
                    user_record = user_record.iloc[0]
                    # Compare passwords after stripping potential whitespace
                    if str(user_record['Password']).strip() == password.strip():
                        # Role check logic
                        if role_check and str(user_record['Role']).strip() != role_check:
                            st.error(f"Access Denied. You do not have '{role_check}' permissions.")
                        elif str(user_record['Status']).strip() == 'Approved':
                            st.session_state.logged_in = True
                            st.session_state.user_role = str(user_record['Role']).strip()
                            st.session_state.user_name = str(user_record['FullName']).strip()
                            st.rerun()
                        else:
                            st.warning("Your account is not yet approved by an admin.")
                    else:
                        st.error("Incorrect password. Please try again.")

            except Exception as e:
                st.error(f"An error occurred during login: {e}")


def signup_form(db_connector, sheet_url, worksheet_name):
    """Creates a signup form and handles new user registration."""
    with st.form(key="signup_form"):
        # Form fields (truncated for brevity)
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
            
            try:
                user_sheet = db_connector.get_worksheet(sheet_url, worksheet_name)
                users_df = db_connector.get_dataframe(user_sheet)

                if not users_df.empty and phone_login.strip() in users_df['Phone(login)'].astype(str).str.strip().values:
                    st.error("This phone number is already registered. Please log in.")
                    return

                new_user_data = [
                    full_name, college, branch, reg_no, pass_year, phone_login,
                    phone_whatsapp, email, password, "Not Approved", "Student",
                    experience, brief_presenter, linkedin, github, interest_area
                ]
                
                db_connector.append_record(user_sheet, new_user_data)
                st.success("Registration successful! An admin will approve your account shortly.")

            except Exception as e:
                st.error(f"An error occurred during signup: {e}")


def menu(db_connector):
    """Displays the sidebar menu based on user role."""
    st.sidebar.success(f"Welcome, {st.session_state.user_name}!")
    st.sidebar.write(f"Your Role: **{st.session_state.user_role}**")
    
    # Define pages accessible to all roles
    page_options = {
        "🏠 User Home": user_main,
        "🎤 Live Session": seminar_session_main,
    }

    # Add role-specific pages
    user_role = st.session_state.user_role
    if user_role == 'Admin':
        page_options["👑 Admin Dashboard"] = admin_main
    # If a user is a 'Lead', they are also an 'Organizer'
    if user_role in ['Organizer', 'Lead']:
        page_options["📝 Organizer Dashboard"] = organizer_main

    selection = st.sidebar.radio("Go to", list(page_options.keys()))
    
    # Render the selected page, passing the connector
    page_function = page_options[selection]
    try:
        page_function(db_connector)
    except TypeError:
         st.error(f"The page '{selection}' is not correctly configured to receive the database connection. Please update its main function.")
         # Fallback for pages that might not have been updated yet
         page_function()


    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Entry point of the app ---
if __name__ == "__main__":
    main()

