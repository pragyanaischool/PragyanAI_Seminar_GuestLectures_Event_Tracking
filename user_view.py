import streamlit as st
import pandas as pd

# --- Constants ---
SEMINAR_DATA_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
SEMINAR_WORKSHEET_NAME = "SeminarEvents"
USER_DATA_URL = "https://docs.google.com/spreadsheets/d/1nJq-DCS-bGMqtaVvU9VImWhOEet5uuL-uQHcMKBgSss/edit?usp=sharing"
USER_WORKSHEET_NAME = "Users"

def user_main(db_connector):
    """
    The main function for the User Home page.
    """
    # --- Improved Header Section ---
    col1, col2 = st.columns([1, 4])
    with col1:
        try:
            st.image("PragyanAI_Transperent.png", width=150)
        except Exception as e:
            pass  # Logo is optional here
    with col2:
        st.title("Guest Lecture and Seminar Platform")
        st.subheader("🏠 Home")

    st.write(f"Welcome to the PragyanAI Seminar Platform, {st.session_state.user_name}!")
    st.info("Here you can manage your seminar enrollments and view upcoming events.")
    st.divider()

    # --- Fetch Data ---
    seminar_sheet = db_connector.get_worksheet(SEMINAR_DATA_URL, SEMINAR_WORKSHEET_NAME)
    seminars_df = db_connector.get_dataframe(seminar_sheet)

    user_sheet = db_connector.get_worksheet(USER_DATA_URL, USER_WORKSHEET_NAME)
    users_df = db_connector.get_dataframe(user_sheet)
    
    # NOTE: Assumes user's phone number is stored in session state upon login.
    # This might require a small change in 'app.py'.
    user_phone = st.session_state.get('user_phone', None)
    
    if not user_phone or users_df.empty:
        st.error("Could not retrieve user session information. Please try logging out and back in.")
        return

    try:
        current_user = users_df[users_df['Phone(login)'].astype(str) == user_phone].iloc[0]
        enrolled_seminars_str = current_user.get('EnrolledSeminars', '')
        enrolled_seminars = enrolled_seminars_str.split(',') if enrolled_seminars_str else []
    except (IndexError, KeyError):
        st.error("Could not find your user record. Please contact an admin.")
        return

    # --- Tabbed Layout ---
    tab1, tab2, tab3 = st.tabs(["🗓️ All Upcoming", "✅ My Enrolled Seminars", "🔍 Available to Enroll"])

    with tab1:
        st.header("All Upcoming Seminars")
        display_seminars(seminars_df, "all", enrolled_seminars, db_connector, user_sheet, user_phone)

    with tab2:
        st.header("Seminars You Are Enrolled In")
        enrolled_df = seminars_df[seminars_df['Seminar Title'].isin(enrolled_seminars)]
        display_seminars(enrolled_df, "enrolled", enrolled_seminars, db_connector, user_sheet, user_phone)

    with tab3:
        st.header("Seminars Available for Enrollment")
        not_enrolled_df = seminars_df[~seminars_df['Seminar Title'].isin(enrolled_seminars)]
        display_seminars(not_enrolled_df, "not_enrolled", enrolled_seminars, db_connector, user_sheet, user_phone)


def display_seminars(df, view_type, enrolled_list, db_connector, user_sheet, user_phone):
    """Helper function to display seminars in a consistent format."""
    if df.empty:
        if view_type == "enrolled":
            st.info("You haven't enrolled in any upcoming seminars yet. Check the 'Available to Enroll' tab!")
        elif view_type == "not_enrolled":
            st.success("You are enrolled in all available seminars. Great job!")
        else:
            st.success("✔️ No upcoming seminars scheduled. Please check back later!")
        return

    for index, row in df.iterrows():
        seminar_title = row.get('Seminar Title', 'No Title')
        with st.container(border=True):
            st.subheader(seminar_title)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Date", str(row.get('Date', 'TBA')))
            col2.metric("Time", str(row.get('Time', 'TBA')))
            col3.metric("Presenter", str(row.get('Presenter Name(s)', 'N/A')))
            
            st.markdown(f"**Description:** {row.get('Seminar Description', 'No description available.')}")
            st.divider()

            # --- Action Buttons ---
            if view_type == "enrolled":
                st.info("✅ You are enrolled. To join, go to the **'Live Session'** page from the sidebar.")
            else: # For 'all' and 'not_enrolled' views
                if seminar_title in enrolled_list:
                    st.success("✔️ You are already enrolled in this seminar.")
                else:
                    if st.button("✍️ Enroll Now", key=f"enroll_{seminar_title}_{view_type}"):
                        handle_enrollment(seminar_title, enrolled_list, db_connector, user_sheet, user_phone)


def handle_enrollment(seminar_title, current_enrollments, db_connector, user_sheet, user_phone):
    """Handles the logic to enroll a user in a seminar."""
    new_enrollments = current_enrollments + [seminar_title]
    new_enrollments_str = ",".join(new_enrollments)
    
    update_data = {'EnrolledSeminars': new_enrollments_str}
    
    if db_connector.update_record(user_sheet, 'Phone(login)', user_phone, update_data):
        st.success(f"Successfully enrolled in '{seminar_title}'! The page will now refresh.")
        st.rerun()
    else:
        st.error("Failed to enroll. Please try again or contact an administrator.")
        
