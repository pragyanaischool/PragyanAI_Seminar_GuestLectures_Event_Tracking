import streamlit as st
import pandas as pd
from datetime import datetime

def organizer_main(db_connector):
    """The main function for the Organizer Dashboard page."""
    st.header("📝 Organizer Dashboard")

    # --- Add Refresh Button ---
    if st.button("🔄 Refresh Data"):
        # Clear the cache for the database connection and worksheets
        st.cache_resource.clear()
        st.success("Data has been refreshed!")
        st.rerun() # Rerun the app to fetch the latest data

    # Define constants for Google Sheets
    SEMINAR_SHEET_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
    SEMINAR_WORKSHEET_NAME = "Seminar_Guest_Event_List"
    USER_DATA_URL = "https://docs.google.com/spreadsheets/d/1nJq-DCS-bGMqtaVvU9VImWhOEet5uuL-uQHcMKBgSss/edit?usp=sharing"
    
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Create New Event",
        "📅 Your Submitted Events",
        "✏️ Update Your Events",
        "👥 List Candidates per Event"
    ])

    # --- Tab 1: Create a New Seminar Event ---
    with tab1:
        st.subheader("Create a New Seminar Event")
        with st.form(key="create_event_form", clear_on_submit=True):
            event_name = st.text_input("Seminar/Event Name *")
            event_date = st.date_input("Event Date *")
            domain = st.text_input("Domain (e.g., AI/ML, Web Development) *")
            description = st.text_area("Brief Description *")
            external_url = st.text_input("External URL (for more info)")
            whatsapp_link = st.text_input("WhatsApp Group Link")
            meet_link = st.text_input("Google Meet / Session Link")
            evaluation_link = st.text_input("Seminar Evaluation Google Form Link") # Changed field

            submit_button = st.form_submit_button("Submit for Approval")

            if submit_button:
                if not all([event_name, event_date, domain, description]):
                    st.warning("Please fill in all required fields.")
                else:
                    seminar_sheet = db_connector.get_worksheet(SEMINAR_SHEET_URL, SEMINAR_WORKSHEET_NAME)
                    if seminar_sheet:
                        new_seminar_data = [
                            event_date.strftime("%Y-%m-%d"),
                            event_name,
                            domain,
                            description,
                            external_url,
                            "Not Approved",
                            "Upcoming",
                            whatsapp_link,
                            meet_link,
                            "", # Placeholder for Seminar_GuestLecture_Sheet_Link
                            evaluation_link,
                            "", "", "", # Placeholders for sample links
                            st.session_state.user_name # Organizer_Name
                        ]
                        try:
                            success = db_connector.add_record(seminar_sheet, new_seminar_data)
                            if success:
                                st.success(f"Successfully submitted '{event_name}' for approval!")
                            else:
                                st.error("Failed to submit the event. Please check the logs.")
                        except Exception as e:
                            st.error(f"An error occurred while creating the event: {e}")

    # --- Tab 2: Your Submitted Events ---
    with tab2:
        st.subheader("Events You Have Submitted")
        seminar_sheet = db_connector.get_worksheet(SEMINAR_SHEET_URL, SEMINAR_WORKSHEET_NAME)
        if seminar_sheet:
            seminars_df = db_connector.get_dataframe(seminar_sheet)
            if not seminars_df.empty and 'Organizer_Name' in seminars_df.columns:
                # Filter events created by the current organizer
                organizer_events = seminars_df[seminars_df['Organizer_Name'] == st.session_state.user_name]
                if not organizer_events.empty:
                    st.dataframe(organizer_events)
                else:
                    st.info("You have not submitted any events yet.")
            else:
                st.info("No events found or 'Organizer_Name' column is missing.")

    # --- Tab 3: Update Your Events ---
    with tab3:
        st.subheader("Update an Event You Created")
        seminar_sheet = db_connector.get_worksheet(SEMINAR_SHEET_URL, SEMINAR_WORKSHEET_NAME)
        if seminar_sheet:
            seminars_df = db_connector.get_dataframe(seminar_sheet)
            if not seminars_df.empty and 'Organizer_Name' in seminars_df.columns:
                organizer_events = seminars_df[seminars_df['Organizer_Name'] == st.session_state.user_name]
                if not organizer_events.empty:
                    event_to_update = st.selectbox(
                        "Select an event to update",
                        options=organizer_events['Seminar_Event_Name'].tolist(),
                        key="update_event_select"
                    )
                    if event_to_update:
                        event_details = organizer_events[organizer_events['Seminar_Event_Name'] == event_to_update].iloc[0]
                        with st.form(key="update_event_form"):
                            st.write(f"**Updating:** {event_details['Seminar_Event_Name']}")
                            
                            # Create form fields with existing data as default values
                            updated_description = st.text_area("Brief Description", value=event_details.get('BriefDescription', ''))
                            updated_whatsapp = st.text_input("WhatsApp Link", value=event_details.get('WhatsappLink', ''))
                            updated_meet = st.text_input("Meet Session Link", value=event_details.get('Meet_session_Link', ''))
                            updated_eval = st.text_input("Evaluation Form Link", value=event_details.get('Seminar Evaluation-GoogleFormLink', ''))
                            
                            update_button = st.form_submit_button("Update Event Details")

                            if update_button:
                                update_data = {
                                    'BriefDescription': updated_description,
                                    'WhatsappLink': updated_whatsapp,
                                    'Meet_session_Link': updated_meet,
                                    'Seminar Evaluation-GoogleFormLink': updated_eval
                                }
                                success = db_connector.update_record(
                                    seminar_sheet,
                                    lookup_col='Seminar_Event_Name',
                                    lookup_val=event_to_update,
                                    update_data=update_data
                                )
                                if success:
                                    st.success(f"Successfully updated '{event_to_update}'!")
                                else:
                                    st.error("Failed to update the event.")
                else:
                    st.info("You have no events to update.")

    # --- Tab 4: List Candidates per Event ---
    with tab4:
        st.subheader("View Enrolled Candidates for Your Events")
        seminar_sheet = db_connector.get_worksheet(SEMINAR_SHEET_URL, SEMINAR_WORKSHEET_NAME)
        if seminar_sheet:
            seminars_df = db_connector.get_dataframe(seminar_sheet)
            if not seminars_df.empty and 'Organizer_Name' in seminars_df.columns and 'Approved_Status' in seminars_df.columns:
                # --- MODIFIED: Filter logic to check for 'Yes' instead of 'Approved' ---
                approved_organizer_events = seminars_df[
                    (seminars_df['Organizer_Name'] == st.session_state.user_name) &
                    (seminars_df['Approved_Status'] == 'Yes')
                ]
                if not approved_organizer_events.empty:
                    event_to_view = st.selectbox(
                        "Select an approved event to see enrollments",
                        options=approved_organizer_events['Seminar_Event_Name'].tolist(),
                        key="view_enrollments_select"
                    )
                    if event_to_view:
                        event_details = approved_organizer_events[approved_organizer_events['Seminar_Event_Name'] == event_to_view].iloc[0]
                        enrollment_sheet_link = event_details.get('Seminar_GuestLecture_Sheet_Link')

                        if enrollment_sheet_link and "docs.google.com/spreadsheets" in enrollment_sheet_link:
                            with st.spinner("Fetching enrollment data..."):
                                try:
                                    # We need to guess the name of the tab in the target sheet.
                                    # Common names are 'Sheet1' or 'Enrollments' or in your case 'Presentor_FullName'.
                                    # This is a point of failure if the name is inconsistent.
                                    enrollment_ws = db_connector.get_worksheet(enrollment_sheet_link, "Presentor_FullName")
                                    if enrollment_ws:
                                        enrollments_df = db_connector.get_dataframe(enrollment_ws)
                                        st.write(f"**Enrolled Candidates for '{event_to_view}'**")
                                        st.dataframe(enrollments_df)
                                    else:
                                        st.warning("Could not access the enrollment worksheet. Check the link and ensure a 'Presentor_FullName' tab exists.")
                                except Exception as e:
                                    st.error(f"Failed to load enrollment data. The link might be incorrect or the sheet structure is not as expected. Error: {e}")
                        else:
                            st.info("No enrollment sheet link provided for this event.")
                else:
                    st.info("You have no approved events to view candidates for.")
