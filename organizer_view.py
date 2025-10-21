import streamlit as st
import pandas as pd

def organizer_main(db_connector):
    """The main function for the Organizer Dashboard page."""
    st.title("📝 Organizer Dashboard")
    st.info("Create and manage seminar events from this dashboard.")

    # --- Constants for Google Sheets ---
    SEMINAR_DATA_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
    SEMINAR_WORKSHEET_NAME = "SeminarEvents"

    # --- Fetch Data ---
    seminar_sheet = db_connector.get_worksheet(SEMINAR_DATA_URL, SEMINAR_WORKSHEET_NAME)
    if not seminar_sheet:
        st.error("Failed to connect to the Seminar Events database. Please contact an admin.")
        return

    seminars_df = db_connector.get_dataframe(seminar_sheet)

    # --- Main Organizer Tabs ---
    create_tab, manage_tab = st.tabs(["Create New Event", "Manage Your Events"])

    with create_tab:
        st.header("Create a New Seminar Event")
        with st.form("new_seminar_form", clear_on_submit=True):
            title = st.text_input("Seminar Title *")
            date = st.date_input("Date *")
            time = st.time_input("Time *")
            presenter = st.text_input("Presenter Name(s) *", value=st.session_state.get('user_name', ''))
            description = st.text_area("Seminar Description")
            meet_link = st.text_input("Google Meet / Other Link")
            slides_link = st.text_input("Google Slides Link (Shareable)")

            submitted = st.form_submit_button("Create Event")

            if submitted:
                if not all([title, date, time, presenter]):
                    st.warning("Please fill in all required fields marked with *.")
                else:
                    # Match the column order in the Google Sheet
                    new_event_data = [
                        title, str(date), str(time), presenter, description,
                        "",  # Placeholder for Admin-filled WhatsApp Link
                        meet_link, slides_link, "Pending"  # Default status
                    ]
                    if db_connector.add_record(seminar_sheet, new_event_data):
                        st.success(f"Seminar '{title}' created successfully! An admin will approve it shortly.")
                    else:
                        st.error("Failed to create the seminar event.")

    with manage_tab:
        st.header("Your Created Seminar Events")
        if seminars_df.empty:
            st.info("You have not created any events yet.")
        else:
            # Filter to show events created by the current user
            organizer_events = seminars_df[seminars_df['Presenter Name(s)'] == st.session_state.get('user_name')]
            if organizer_events.empty:
                st.info("You have not created any events yet.")
            else:
                st.dataframe(organizer_events)
