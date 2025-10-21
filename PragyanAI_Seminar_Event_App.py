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

# --- [TOGGLE] Set to True to use local dummy data, False to use live Google Sheets data ---
USE_DUMMY_DATA = False
# -----------------------------------------------------------------------------------------


def load_dummy_data():
    """Generates and returns sample dataframes for offline testing."""
    st.info("App is currently running in **Dummy Data Mode**. No live data is being used.", icon="ℹ️")
    
    # Dummy Admins DataFrame
    admins_data = {
        'Phone(login)': ['9741007422'],
        'UserName': ['SateeshAmbesange'],
        'Password': ['Kanasu@1976']
    }
    admins_df = pd.DataFrame(admins_data)

    # Dummy Users DataFrame
    users_data = {
        'FullName': ['Test User', 'Lead User', 'Pending User'],
        'Phone(login)': ['1111111111', '2222222222', '3333333333'],
        'Password': ['test', 'lead', 'pending'],
        'Status': ['Approved', 'Approved', 'Not Approved'],
        'Role': ['Student', 'Lead', 'Student'],
        'CollegeName': ['N/A', 'N/A', 'N/A'],
        'Branch': ['N/A', 'N/A', 'N/A'],
        'RollNO(UniversityRegNo)': ['N/A', 'N/A', 'N/A'],
        'YearofPassing_Passed': ['N/A', 'N/A', 'N/A'],
        'Phone(Whatsapp)': ['N/A', 'N/A', 'N/A'],
        'Email': ['test@example.com', 'lead@example.com', 'pending@example.com'],
        'Experience': ['None', '5 Years', 'None'],
        'Brief_Presentor': ['N/A', 'N/A', 'N/A'],
        'LinkedinProfile': ['N/A', 'N/A', 'N/A'],
        'Github_Profile': ['N/A', 'N/A', 'N/A'],
        'Area_of_Interest': ['AI', 'ML', 'Web Dev']
    }
    users_df = pd.DataFrame(users_data)
    
    # Return dummy data and None for sheet instances and connector
    return admins_df, users_df, None, None


def main():
    """Main function to run the Streamlit app."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("PragyanAI_Transperent.png", use_container_width=True)
        except Exception:
            st.warning("Logo not found. Please add 'PragyanAI_Transperent.png' to the root directory.")

    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.title("Guest Lecture and Seminar Platform")

    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_name = None
        st.session_state.selected_seminar_title = None

    db_connector = None
    
    if USE_DUMMY_DATA:
        # Initialize dummy data in session state if it doesn't exist
        if 'dummy_admins_df' not in st.session_state:
            st.session_state.dummy_admins_df, st.session_state.dummy_users_df, _, _ = load_dummy_data()
        
        admins_df = st.session_state.dummy_admins_df
        users_df = st.session_state.dummy_users_df
        admin_sheet = None
        user_sheet = None
    else:
        try:
            db_connector = GoogleSheetsConnector()
            SHEET_URL = "https://docs.google.com/spreadsheets/d/1nJq-DCS-bGMqtaVvU9VImWhOEet5uuL-uQHcMKBgSss/edit?usp=sharing"
            admin_sheet = db_connector.get_worksheet(SHEET_URL, "Admins")
            user_sheet = db_connector.get_worksheet(SHEET_URL, "Users")
            admins_df = db_connector.get_dataframe(admin_sheet)
            users_df = db_connector.get_dataframe(user_sheet)
        except Exception as e:
            st.error(f"Failed to connect to the database. Check secrets and sheet names. Error: {e}")
            return

    if not st.session_state.logged_in:
        login_signup_forms(db_connector, admin_sheet, user_sheet, admins_df, users_df)
    else:
        menu(db_connector)


def login_signup_forms(db_connector, admin_sheet, user_sheet, admins_df, users_df):
    """Displays the login and signup forms in tabs."""
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        admin_login_col, user_login_col = st.columns(2)
        with admin_login_col:
            st.header("Admin Login")
            login_form(admins_df, role_check='Admin')
        with user_login_col:
            st.header("User / Organizer Login")
            login_form(users_df, role_check=None)

    with signup_tab:
        st.header("Create a New Account")
        signup_form(db_connector, user_sheet, users_df)


def login_form(data_df, role_check=None):
    """Creates a login form and handles authentication using a dataframe."""
    form_key = f"login_form_{role_check or 'user'}"
    with st.form(key=form_key):
        phone = st.text_input("Phone Number (Login ID)")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button(label="Login")

        if submit_button:
            if not phone or not password:
                st.warning("Please enter both phone and password.")
                return

            sheet_name = 'Admins' if role_check else 'Users'
            required_columns = ['Phone(login)', 'Password', 'UserName'] if role_check else ['Phone(login)', 'Password', 'Status', 'Role', 'FullName']

            if data_df is None or not all(col in data_df.columns for col in required_columns):
                st.error(f"The '{sheet_name}' data is not available or is missing required columns: {', '.join(required_columns)}.")
                return

            user_record = data_df[data_df['Phone(login)'].astype(str).str.strip() == phone.strip()]

            if user_record.empty:
                st.error("User not found. Check phone number or sign up.")
            else:
                user_record = user_record.iloc[0]
                if str(user_record['Password']).strip() == password.strip():
                    if role_check == 'Admin':
                        st.session_state.logged_in = True
                        st.session_state.user_role = 'Admin'
                        st.session_state.user_name = str(user_record['UserName']).strip()
                        st.rerun()
                    elif str(user_record['Status']).strip() == 'Approved':
                        st.session_state.logged_in = True
                        st.session_state.user_role = str(user_record['Role']).strip()
                        st.session_state.user_name = str(user_record['FullName']).strip()
                        st.rerun()
                    else:
                        st.warning("Your account is not yet approved by an admin.")
                else:
                    st.error("Incorrect password.")


def signup_form(db_connector, user_sheet, users_df):
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
            
            # --- MODIFIED: Handle signup in Dummy Data Mode ---
            if USE_DUMMY_DATA:
                if users_df is not None and not users_df.empty and phone_login.strip() in users_df['Phone(login)'].astype(str).str.strip().values:
                    st.error("This phone number is already registered in the dummy data.")
                    return
                
                new_user_record = {
                    'FullName': [full_name], 'Phone(login)': [phone_login], 'Password': [password],
                    'Status': ["Not Approved"], 'Role': ["Student"], 'CollegeName': [college or 'N/A'],
                    'Branch': [branch or 'N/A'], 'RollNO(UniversityRegNo)': [reg_no or 'N/A'],
                    'YearofPassing_Passed': [pass_year or 'N/A'], 'Phone(Whatsapp)': [phone_whatsapp or 'N/A'],
                    'Email': [email], 'Experience': [experience or 'N/A'], 'Brief_Presentor': [brief_presenter or 'N/A'],
                    'LinkedinProfile': [linkedin or 'N/A'], 'Github_Profile': [github or 'N/A'],
                    'Area_of_Interest': [interest_area or 'N/A']
                }
                new_user_df = pd.DataFrame(new_user_record)
                
                st.session_state.dummy_users_df = pd.concat([st.session_state.dummy_users_df, new_user_df], ignore_index=True)
                st.success("Dummy user registered successfully! The account is 'Not Approved' by default.")
                return

            # --- Live Data Signup Logic ---
            try:
                if users_df is not None and not users_df.empty and phone_login.strip() in users_df['Phone(login)'].astype(str).str.strip().values:
                    st.error("This phone number is already registered.")
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
    
    page_options = { "🏠 User Home": user_main, "🎤 Live Session": seminar_session_main }

    user_role = st.session_state.user_role
    if user_role == 'Admin':
        page_options["👑 Admin Dashboard"] = admin_main
        page_options["📝 Organizer Dashboard"] = organizer_main
    elif user_role in ['Organizer', 'Lead']:
        page_options["📝 Organizer Dashboard"] = organizer_main

    selection = st.sidebar.radio("Go to", list(page_options.keys()))
    page_function = page_options[selection]
    
    try:
        page_function(db_connector)
    except Exception as e:
        if USE_DUMMY_DATA:
             st.warning(f"Note: Some page features might be limited in Dummy Data Mode.")
             try:
                 page_function()
             except TypeError:
                 st.error(f"The page '{selection}' requires a live database connection and cannot run in Dummy Data Mode.")
        else:
            st.error(f"Error loading page '{selection}': {e}")

    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()

