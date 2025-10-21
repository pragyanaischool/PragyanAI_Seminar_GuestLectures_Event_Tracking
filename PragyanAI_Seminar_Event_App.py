import streamlit as st
from admin_view import admin_main
from organizer_view import organizer_main
from user_view import user_main
from seminar_session import seminar_session_main
from evaluation import evaluation_main
from quiz import quiz_main
from google_sheets_db import connect_to_sheet, get_user_db, get_users_df, add_user

def main():
    st.set_page_config(page_title="Seminar Platform", layout="wide")
    
    # Add logo at the top.
    try:
        st.image("PragyanAI_Transperent.png", width=200)
    except Exception as e:
        st.warning("Logo image not found. Please add 'PragyanAI_Transperent.png' to your project directory.")

    st.title("Guest Lecture and Seminar Platform")

    # This application connects to the Google Sheet for user data:
    # https://docs.google.com/spreadsheets/d/1nJq-DCS-bGMqtaVvU9VImWhOEet5uuL-uQHcMKBgSss
    # IMPORTANT: Ensure the sheet has a worksheet named "Users" and is shared with your service account email.

    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_name = None

    # Connect to Google Sheets
    client = connect_to_sheet()
    if not client:
        st.stop()
    
    user_sheet = get_user_db(client)
    if not user_sheet:
        st.stop()

    if not st.session_state.logged_in:
        # Create tabs for different login types and signup
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

        with login_tab:
            st.subheader("Login to Your Account")
            login_form(user_sheet)

        with signup_tab:
            st.subheader("Create a New Account")
            signup_form(user_sheet)
    else:
        st.sidebar.write(f"Welcome, {st.session_state.user_name}!")
        st.sidebar.write(f"Role: {st.session_state.user_role}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.user_name = None
            st.experimental_rerun()
        
        menu()

def login_form(worksheet):
    users_df = get_users_df(worksheet)

    with st.form("login_form"):
        phone_number = st.text_input("Phone Number (Login ID)")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if not users_df.empty:
                # Ensure phone number is treated as a string for comparison
                user_record = users_df[users_df['Phone(login)'].astype(str) == str(phone_number)]
                
                if not user_record.empty:
                    user_record = user_record.iloc[0]
                    if user_record['Password'] == password:
                        if user_record['Status'] == 'Approved':
                            st.session_state.logged_in = True
                            st.session_state.user_role = user_record['Role']
                            st.session_state.user_name = user_record['FullName']
                            st.experimental_rerun()
                        else:
                            st.error("Your account is not approved yet. Please wait for admin approval.")
                    else:
                        st.error("Incorrect password.")
                else:
                    st.error("User not found. Please check your phone number or sign up.")
            else:
                st.error("Could not fetch user data from the database.")


def signup_form(worksheet):
    with st.form("signup_form"):
        st.write("Please fill in your details to register. Fields with * are required.")
        
        # Collecting user details as per the Google Sheet columns
        full_name = st.text_input("Full Name*")
        college_name = st.text_input("College Name*")
        branch = st.text_input("Branch*")
        roll_no = st.text_input("University Reg No*")
        year_of_passing = st.text_input("Year of Passing*")
        phone_login = st.text_input("Phone (for login)*")
        phone_whatsapp = st.text_input("Phone (for Whatsapp)")
        username = st.text_input("Username")
        password = st.text_input("Password*", type="password")
        experience = st.text_area("Experience (if any)")
        brief_presenter = st.text_area("Brief about yourself as a presenter")
        linkedin = st.text_input("LinkedIn Profile URL")
        github = st.text_input("GitHub Profile URL")
        area_of_interest = st.text_area("Area of Interest*")

        submitted = st.form_submit_button("Sign Up")
        
        if submitted:
            if not all([full_name, college_name, branch, roll_no, year_of_passing, phone_login, password, area_of_interest]):
                st.warning("Please fill in all the required fields marked with *.")
            else:
                # Check if user already exists
                users_df = get_users_df(worksheet)
                if not users_df[users_df['Phone(login)'].astype(str) == str(phone_login)].empty:
                    st.error("A user with this phone number already exists. Please login.")
                    return

                new_user = {
                    "FullName": full_name,
                    "CollegeName": college_name,
                    "Branch": branch,
                    "RollNO(UniversityRegNo)": roll_no,
                    "YearofPassing_Passed": year_of_passing,
                    "Phone(login)": phone_login,
                    "Phone(Whatsapp)": phone_whatsapp,
                    "UserName": username,
                    "Password": password,
                    "Status": "NotApproved",
                    "Role": "Student",
                    "Experience": experience,
                    "Brief_Presentor": brief_presenter,
                    "LinkedinProfile": linkedin,
                    "Github_Profile": github,
                    "Area_of_Interest": area_of_interest
                }
                
                if add_user(worksheet, new_user):
                    st.balloons()
                    st.success("Registration successful! Your account is pending approval from the admin.")
                else:
                    st.error("Registration failed. There was an issue connecting to the database.")


def menu():
    st.sidebar.title("Navigation")
    
    # Common pages for all logged-in users
    base_pages = ["View Seminars", "Live Seminar", "Evaluation", "Quiz"]
    
    if st.session_state['user_role'] == "Admin":
        # Admin sees all pages, with their dashboard first
        pages = ["Admin Dashboard", "Create Seminar"] + base_pages
        page = st.sidebar.radio("Go to", pages)
        
        if page == "Admin Dashboard":
            admin_main()
        elif page == "Create Seminar":
            organizer_main()

    elif st.session_state['user_role'] in ["Organizer", "Lead"]:
        # Organizers can create and view seminars
        pages = ["Create Seminar"] + base_pages
        page = st.sidebar.radio("Go to", pages)

        if page == "Create Seminar":
            organizer_main()
            
    else: # Default for "Student", "User", or any other role
        pages = base_pages
        page = st.sidebar.radio("Go to", pages)

    # Handle navigation for common pages
    if page == "View Seminars":
        user_main()
    elif page == "Live Seminar":
        seminar_session_main()
    elif page == "Evaluation":
        evaluation_main()
    elif page == "Quiz":
        quiz_main()

if __name__ == "__main__":
    main()
