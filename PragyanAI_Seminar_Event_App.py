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
    st.title("Guest Lecture and Seminar Platform")

    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_email = None

    # Connect to Google Sheets
    client = connect_to_sheet()
    if not client:
        st.stop()
    
    user_sheet = get_user_db(client)
    if not user_sheet:
        st.stop()

    if not st.session_state.logged_in:
        auth_choice = st.radio("Choose Action", ["Login", "Sign Up"], horizontal=True)
        if auth_choice == "Login":
            login_form(user_sheet)
        else:
            signup_form(user_sheet)
    else:
        st.sidebar.write(f"Welcome, {st.session_state.user_email}!")
        st.sidebar.write(f"Role: {st.session_state.user_role}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.user_email = None
            st.experimental_rerun()
        
        menu()

def login_form(worksheet):
    st.header("Login")
    users_df = get_users_df(worksheet)

    with st.form("login_form"):
        phone_number = st.text_input("Phone Number (Login ID)")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if not users_df.empty:
                user_record = users_df[users_df['Phone(login)'].astype(str) == phone_number]
                
                if not user_record.empty:
                    user_record = user_record.iloc[0]
                    if user_record['Password'] == password:
                        if user_record['Status'] == 'Approved':
                            st.session_state.logged_in = True
                            st.session_state.user_role = user_record['Role']
                            st.session_state.user_email = user_record['FullName'] # Using name as identifier
                            st.experimental_rerun()
                        else:
                            st.error("Your account is not approved yet. Please contact the admin.")
                    else:
                        st.error("Incorrect password.")
                else:
                    st.error("User not found.")
            else:
                st.error("Could not fetch user data.")

def signup_form(worksheet):
    st.header("Sign Up")
    with st.form("signup_form"):
        st.write("Please fill in your details to register.")
        
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
                    st.success("Registration successful! Your account is pending approval from the admin.")
                else:
                    st.error("Registration failed. Please try again.")


def menu():
    st.sidebar.title("Navigation")
    
    if st.session_state['user_role'] == "Admin":
        page = st.sidebar.radio("Go to", ["Admin Dashboard", "Create Seminar", "View Seminars", "Live Seminar", "Evaluation", "Quiz"])
        if page == "Admin Dashboard":
            admin_main()
        elif page == "Create Seminar":
            organizer_main()
        elif page == "View Seminars":
            user_main()
        elif page == "Live Seminar":
            seminar_session_main()
        elif page == "Evaluation":
            evaluation_main()
        elif page == "Quiz":
            quiz_main()

    elif st.session_state['user_role'] in ["Organizer", "Lead"]:
        page = st.sidebar.radio("Go to", ["Create Seminar", "View Seminars", "Live Seminar", "Evaluation", "Quiz"])
        if page == "Create Seminar":
            organizer_main()
        elif page == "View Seminars":
            user_main()
        elif page == "Live Seminar":
            seminar_session_main()
        elif page == "Evaluation":
            evaluation_main()
        elif page == "Quiz":
            quiz_main()
            
    elif st.session_state['user_role'] == "User":
        page = st.sidebar.radio("Go to", ["View Seminars", "Live Seminar", "Evaluation", "Quiz"])
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
