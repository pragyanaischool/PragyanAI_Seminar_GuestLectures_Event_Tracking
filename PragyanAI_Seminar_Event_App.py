import streamlit as st
import pandas as pd
#from google_sheets_db import GoogleSheetsDB
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

    # Connect to Google Sheets
    try:
        # Using the correct sheet name as confirmed
        user_sheet_name = "PragyanAI-Seminar-GuestLeacture_Event_UserData"
        user_db = GoogleSheetsDB(st.secrets["gcp_service_account"], user_sheet_name)
        user_sheet = user_db.worksheet("Users") # The tab name inside the sheet
    except Exception as e:
        st.error(f"Failed to connect to the user database. Please check your Google Sheets setup and secrets. Error: {e}")
        return

    # --- Login/Signup/Main App View Logic ---
    if not st.session_state.logged_in:
        login_signup_forms(user_sheet)
    else:
        # Display the main application menu and content
        menu()

def login_signup_forms(user_sheet):
    """Displays the login and signup forms in tabs."""
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        admin_login_form, user_login_form = st.columns(2)
        with admin_login_form:
            st.header("Admin Login")
            login_form(user_sheet, role_check='Admin')
        with user_login_form:
            st.header("User / Organizer Login")
            login_form(user_sheet, role_check=None) # Allows any approved user

    with signup_tab:
        st.header("Create a New Account")
        signup_form(user_sheet)


def login_form(user_sheet, role_check=None):
    """Creates a login form and handles authentication."""
    with st.form(key=f"login_form_{role_check or 'user'}"):
        phone = st.text_input("Phone Number (Login ID)")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button(label="Login")

        if submit_button:
            if not phone or not password:
                st.warning("Please enter both phone number and password.")
                return

            try:
                users_df = pd.DataFrame(user_sheet.get_all_records())

                # --- Data Validation ---
                required_columns = ['Phone(login)', 'Password', 'Status', 'Role', 'FullName']
                missing_columns = [col for col in required_columns if col not in users_df.columns]
                if missing_columns:
                    st.error(f"The 'Users' sheet is missing required columns: {', '.join(missing_columns)}. Please check the sheet headers.")
                    return
                # --- End Validation ---

                if users_df.empty:
                    st.error("User database is currently empty.")
                    return

                user_record = users_df[users_df['Phone(login)'].astype(str) == phone]

                if user_record.empty:
                    st.error("User not found. Please check your phone number or sign up.")
                else:
                    user_record = user_record.iloc[0]
                    if user_record['Password'] == password:
                        # Role check logic
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

            except Exception as e:
                st.error(f"An error occurred during login: {e}")


def signup_form(user_sheet):
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
            
            try:
                users_df = pd.DataFrame(user_sheet.get_all_records())
                if not users_df.empty and phone_login in users_df['Phone(login)'].astype(str).values:
                    st.error("This phone number is already registered. Please log in.")
                    return

                new_user_data = {
                    "FullName": full_name,
                    "CollegeName": college,
                    "Branch": branch,
                    "RollNO(UniversityRegNo)": reg_no,
                    "YearofPassing_Passed": pass_year,
                    "Phone(login)": phone_login,
                    "Phone(Whatsapp)": phone_whatsapp,
                    "Email": email,
                    "Password": password,
                    "Status": "Not Approved",
                    "Role": "Student", # Default role
                    "Experience": experience,
                    "Brief_Presentor": brief_presenter,
                    "LinkedinProfile": linkedin,
                    "Github_Profile": github,
                    "Area_of_Interest": interest_area
                }
                user_sheet.append_row(list(new_user_data.values()))
                st.success("Registration successful! An admin will approve your account shortly.")

            except Exception as e:
                st.error(f"An error occurred during signup: {e}")


def menu():
    """Displays the sidebar menu based on user role and directs them to the appropriate default page."""
    st.sidebar.success(f"Welcome, {st.session_state.user_name}!")
    st.sidebar.write(f"Your Role: **{st.session_state.user_role}**")
    
    # Initialize page options dictionary
    page_options = {}

    # Determine the page order and options based on the user's role
    role = st.session_state.user_role

    if role == 'Admin':
        # Admin sees Admin Dashboard first
        page_options = {
            "👑 Admin Dashboard": admin_main,
            "📝 Organizer Dashboard": organizer_main,
            "🏠 Home": user_main,
            "🎤 Live Session": seminar_session_main,
        }
    elif role in ['Organizer', 'Lead']:
        # Organizer/Lead sees Organizer Dashboard first
        page_options = {
            "📝 Organizer Dashboard": organizer_main,
            "🏠 Home": user_main,
            "🎤 Live Session": seminar_session_main,
        }
    else: # Default for 'Student' or any other role
        # Regular users see the User Home first
        page_options = {
            "🏠 Home": user_main,
            "🎤 Live Session": seminar_session_main,
        }

    selection = st.sidebar.radio("Go to", list(page_options.keys()))
    
    # Render the selected page
    page_function = page_options[selection]
    page_function()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_name = None
        st.rerun()

# --- Entry point of the app ---
if __name__ == "__main__":
    main()
