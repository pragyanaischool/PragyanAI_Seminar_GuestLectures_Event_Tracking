import streamlit as st
from admin_view import admin_main
from organizer_view import organizer_main
from user_view import user_main
from seminar_session import seminar_session_main
from evaluation import evaluation_main
from quiz import quiz_main

# Dummy data for demonstration
USERS = {
    "admin@test.com": {"password": "admin", "role": "Admin"},
    "organizer@test.com": {"password": "organizer", "role": "Organizer"},
    "user@test.com": {"password": "user", "role": "User"}
}

SEMINARS = {}

def main():
    st.set_page_config(page_title="Seminar Platform", layout="wide")
    st.title("Guest Lecture and Seminar Platform")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.session_state['user_email'] = None

    if not st.session_state['logged_in']:
        login_form()
    else:
        st.sidebar.write(f"Welcome, {st.session_state['user_email']}!")
        st.sidebar.write(f"Role: {st.session_state['user_role']}")
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['user_role'] = None
            st.session_state['user_email'] = None
            st.experimental_rerun()
        
        menu()

def login_form():
    st.header("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if email in USERS and USERS[email]['password'] == password:
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = USERS[email]['role']
                st.session_state['user_email'] = email
                st.experimental_rerun()
            else:
                st.error("Invalid email or password")

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

    elif st.session_state['user_role'] == "Organizer":
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
