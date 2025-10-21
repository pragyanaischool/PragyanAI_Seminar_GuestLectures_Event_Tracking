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
    col1, col2 = st.columns([1, 5])
    with col1:
        try:
            st.image("PragyanAI_Transperent.png", width=120)
        except Exception as e:
            pass  # Logo is optional here
    with col2:
        st.title("User View")
        st.write(f"Welcome to the platform, {st.session_state.user_name}!")

    st.info("Here you can manage your seminar enrollments and view upcoming events.")
    st.divider()

    # --- Fetch Data ---
    seminar_sheet = db_connector.get_worksheet(SEMINAR_DATA_URL, SEMINAR_WORKSHEET_NAME)
    seminars_df = db_connector.get_dataframe(seminar_sheet)

    user_sheet = db_connector.get_worksheet(USER_DATA_URL, USER_WORKSHEET_NAME)
    users_df = db_connector.get_dataframe(user_sheet)

    user_phone = st.session_state.get('user_phone', None)

    if not user_phone or users_df.empty:
        st.error("Could not retrieve user session information. Please try logging out and back in.")
        return

    try:
        current_user = users_df[users_df['Phone(login)'].astype(str) == user_phone].iloc[0]
        enrolled_seminars_str = current_user.get('EnrolledSeminars', '')
        enrolled_seminars = [s.strip() for s in enrolled_seminars_str.split(',') if s.strip()]
    except (IndexError, KeyError):
        st.error("Could not find your user record. Please contact an admin.")
        return

    # --- Tabbed Layout ---
    tab1, tab2, tab3 = st.tabs([
        "Upcoming Seminars / Guest Events",
        "Seminars Events - Enrolled",
        "Seminar Events - Yet to Enroll"
    ])

    with tab1:
        st.header("All Upcoming Events")
        display_seminars(seminars_df, "all", enrolled_seminars, db_connector, user_sheet, user_phone)

    with tab2:
        st.header("Events You Are Enrolled In")
        enrolled_df = seminars_df[seminars_df['Seminar Title'].isin(enrolled_seminars)]
        display_seminars(enrolled_df, "enrolled", enrolled_seminars, db_connector, user_sheet, user_phone)

    with tab3:
        st.header("Events Available for Enrollment")
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

            col_info_1, col_info_2, col_info_3 = st.columns(3)
            col_info_1.metric("Date", str(row.get('Date', 'TBA')))
            col_info_2.metric("Time", str(row.get('Time', 'TBA')))
            col_info_3.metric("Presenter", str(row.get('Presenter Name(s)', 'N/A')))

            st.markdown(f"**Description:** {row.get('Seminar Description', 'No description available.')}")
            st.divider()

            # --- Action Buttons ---
            col_action_1, col_action_2 = st.columns(2)
            with col_action_1:
                if seminar_title in enrolled_list:
                    st.success("✔️ You are enrolled")
                else:
                    if st.button("✍️ Enroll Now", key=f"enroll_{seminar_title}_{view_type}", use_container_width=True):
                        handle_enrollment(seminar_title, enrolled_list, db_connector, user_sheet, user_phone)
            
            with col_action_2:
                if st.button("Go to Seminar View ➔", key=f"view_{seminar_title}_{view_type}", use_container_width=True):
                    # Store the selected seminar in session state for the other page to use
                    st.session_state.selected_seminar_title = seminar_title
                    st.info(f"'{seminar_title}' selected. Please navigate to the '🎤 Live Session' page from the sidebar to view details.")


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
        
