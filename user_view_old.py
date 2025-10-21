import streamlit as st
import pandas as pd

def user_main(db_connector):
    """The main function for the User Home page."""
    st.title("🏠 User Home")
    st.info("Here you can manage your seminar enrollments and view upcoming events.")
    st.divider()

    # --- Constants for Google Sheets ---
    SEMINAR_DATA_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
    SEMINAR_WORKSHEET_NAME = "SeminarEvents"
    USER_DATA_URL = "https://docs.google.com/spreadsheets/d/1nJq-DCS-bGMqtaVvU9VImWhOEet5uuL-uQHcMKBgSss/edit?usp=sharing"
    USER_WORKSHEET_NAME = "Users"

    # --- Fetch Data ---
    seminar_sheet = db_connector.get_worksheet(SEMINAR_DATA_URL, SEMINAR_WORKSHEET_NAME)
    user_sheet = db_connector.get_worksheet(USER_DATA_URL, USER_WORKSHEET_NAME)

    if not seminar_sheet or not user_sheet:
        st.error("Failed to connect to databases. Please contact an admin.")
        return

    seminars_df = db_connector.get_dataframe(seminar_sheet)
    users_df = db_connector.get_dataframe(user_sheet)

    if seminars_df.empty:
        st.success("No seminars are scheduled right now. Please check back later!")
        return

    # Filter for only approved seminars
    seminars_df = seminars_df[seminars_df['Status'] == 'Approved']

    user_phone = st.session_state.get('user_phone', None)
    
    try:
        current_user = users_df[users_df['Phone(login)'].astype(str) == str(user_phone)].iloc[0]
        enrolled_seminars_str = current_user.get('EnrolledSeminars', '')
        enrolled_seminars = [s.strip() for s in enrolled_seminars_str.split(',') if s.strip()]
    except (IndexError, KeyError):
        st.error("Could not find your user record. Enrollment features are disabled.")
        enrolled_seminars = []

    # --- Tabbed Layout ---
    tab1, tab2, tab3 = st.tabs([
        "📅 All Upcoming Events",
        "✅ My Enrolled Seminars",
        "✍️ Available to Enroll"
    ])

    with tab1:
        st.header("All Approved Upcoming Events")
        display_seminars(db_connector, user_sheet, user_phone, seminars_df, "all", enrolled_seminars)

    with tab2:
        st.header("Events You Are Enrolled In")
        enrolled_df = seminars_df[seminars_df['Seminar Title'].isin(enrolled_seminars)]
        display_seminars(db_connector, user_sheet, user_phone, enrolled_df, "enrolled", enrolled_seminars)

    with tab3:
        st.header("Events Available for Enrollment")
        not_enrolled_df = seminars_df[~seminars_df['Seminar Title'].isin(enrolled_seminars)]
        display_seminars(db_connector, user_sheet, user_phone, not_enrolled_df, "not_enrolled", enrolled_seminars)

def display_seminars(db_connector, user_sheet, user_phone, df, view_type, enrolled_list):
    """Helper function to display seminars and handle actions."""
    if df.empty:
        st.info("No seminars to display in this category.")
        return

    for index, row in df.iterrows():
        seminar_title = row.get('Seminar Title', 'No Title')
        with st.container(border=True):
            st.subheader(seminar_title)
            col1, col2, col3 = st.columns(3)
            col1.metric("Date", str(row.get('Date', 'TBA')))
            col2.metric("Time", str(row.get('Time', 'TBA')))
            col3.metric("Presenter", str(row.get('Presenter Name(s)', 'N/A')))
            st.markdown(f"**Description:** {row.get('Seminar Description', 'N/A')}")
            
            st.divider()

            col_action_1, col_action_2 = st.columns(2)
            if seminar_title in enrolled_list:
                col_action_1.success("✔️ Enrolled")
            else:
                if col_action_1.button("✍️ Enroll Now", key=f"enroll_{seminar_title}", use_container_width=True):
                    new_enrolled_list = enrolled_list + [seminar_title]
                    new_enrolled_str = ", ".join(new_enrolled_list)
                    if db_connector.update_record(user_sheet, 'Phone(login)', user_phone, {'EnrolledSeminars': new_enrolled_str}):
                        st.success(f"Successfully enrolled in '{seminar_title}'!")
                        st.rerun()
                    else:
                        st.error("Failed to update enrollment.")
            
            if col_action_2.button("Go to Seminar View ➔", key=f"view_{seminar_title}", use_container_width=True):
                st.session_state.selected_seminar_title = seminar_title
                st.info(f"Navigating to '{seminar_title}'. Please select '🎤 Live Session' from the sidebar to view details.")


        
