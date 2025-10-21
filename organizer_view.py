import streamlit as st
import pandas as pd
from datetime import datetime

def organizer_main(db_connector):
    """The main function for the Organizer Dashboard page."""
    st.header("📝 Organizer Dashboard")
    st.markdown("Create, manage, and track your seminar events from this dashboard.")

    # --- Define constants for Google Sheets ---
    SEMINAR_SHEET_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
    SEMINAR_WORKSHEET_NAME = "Seminar_Guest_Event_List"
    
    # Assumes enrollments are tracked in a separate sheet/tab
    ENROLLMENT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1nJq-DCS-bGMqtaVvU9VImWhOEet5uuL-uQHcMKBgSss/edit?usp=sharing"
    ENROLLMENT_WORKSHEET_NAME = "Enrollments"

    # --- Create Tabs for Organizer Functions ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ Create New Event",
        "📄 Your Submitted Events",
        "✏️ Update Your Events",
        "👥 List Candidates"
    ])

    # Fetching seminar data once for all tabs
    try:
        seminar_sheet = db_connector.get_worksheet(SEMINAR_SHEET_URL, SEMINAR_WORKSHEET_NAME)
        seminars_df = db_connector.get_dataframe(seminar_sheet)
        # Filter events created by the current logged-in user
        # NOTE: Assumes a column 'Organizer_Name' exists in the seminar sheet
        if 'Organizer_Name' in seminars_df.columns:
            organizer_events_df = seminars_df[seminars_df['Organizer_Name'] == st.session_state.user_name].copy()
        else:
            # Fallback if the column doesn't exist, show all events with a warning
            organizer_events_df = seminars_df.copy()
            st.sidebar.warning("Sheet is missing 'Organizer_Name' column. Showing all events.")

    except Exception as e:
        st.error(f"Failed to load seminar data. Please check the sheet configuration. Error: {e}")
        # Create empty dataframes to prevent crashes in other tabs
        seminars_df = pd.DataFrame()
        organizer_events_df = pd.DataFrame()


    with tab1:
        st.subheader("Create a New Seminar Event")
        with st.form(key="create_seminar_form", clear_on_submit=True):
            st.write("Fill in the details below to schedule a new seminar. It will be sent to an admin for approval.")
            
            event_name = st.text_input("Seminar Title *")
            event_date = st.date_input("Date of Event *", min_value=datetime.today())
            domain = st.text_input("Domain / Category *")
            description = st.text_area("Brief Description *")
            meet_link = st.text_input("Google Meet / Session Link")
            presentation_link = st.text_input("Google Slides / Presentation Link")
            
            submit_button = st.form_submit_button(label="Submit for Approval")

            if submit_button:
                if not all([event_name, event_date, domain, description]):
                    st.warning("Please fill in all required fields marked with *.")
                else:
                    new_seminar_data = [
                        event_date.strftime("%Y-%m-%d"), event_name, domain, description,
                        "", "Not Approved", "Upcoming", "", meet_link, presentation_link,
                        "", "", "", "", st.session_state.user_name # Append Organizer_Name
                    ]
                    try:
                        db_connector.append_record(seminar_sheet, new_seminar_data)
                        st.success(f"Successfully submitted '{event_name}' for approval!")
                    except Exception as e:
                        st.error(f"An error occurred while creating the event: {e}")

    with tab2:
        st.subheader("Events You Have Submitted")
        if not organizer_events_df.empty:
            st.dataframe(organizer_events_df[['Seminar_Event_Name', 'Event_Date', 'Domain', 'Approved_Status']], use_container_width=True)
        else:
            st.info("You have not submitted any events yet.")

    with tab3:
        st.subheader("Update an Event You've Created")
        if not organizer_events_df.empty:
            event_to_update_name = st.selectbox(
                "Select an event to update",
                options=organizer_events_df['Seminar_Event_Name'].tolist(),
                index=None,
                placeholder="Choose an event..."
            )

            if event_to_update_name:
                event_data = organizer_events_df[organizer_events_df['Seminar_Event_Name'] == event_to_update_name].iloc[0]
                
                with st.form(key="update_event_form"):
                    st.info(f"You are editing: **{event_data['Seminar_Event_Name']}**")
                    
                    updated_date = st.date_input("Date of Event", value=pd.to_datetime(event_data['Event_Date']))
                    updated_domain = st.text_input("Domain / Category", value=event_data.get('Domain', ''))
                    updated_description = st.text_area("Brief Description", value=event_data.get('BriefDescription', ''))
                    updated_meet_link = st.text_input("Google Meet Link", value=event_data.get('Meet_session_Link', ''))
                    updated_slides_link = st.text_input("Google Slides Link", value=event_data.get('Seminar_GuestLecture_Sheet_Link', ''))

                    update_button = st.form_submit_button("Update Event")

                    if update_button:
                        # Find the row index in the original gspread worksheet
                        cell = seminar_sheet.find(event_to_update_name)
                        if cell:
                            row_index = cell.row
                            updates = {
                                'Event_Date': updated_date.strftime("%Y-%m-%d"),
                                'Domain': updated_domain,
                                'BriefDescription': updated_description,
                                'Meet_session_Link': updated_meet_link,
                                'Seminar_GuestLecture_Sheet_Link': updated_slides_link,
                            }
                            db_connector.update_record(seminar_sheet, row_index, updates)
                            st.success(f"Event '{event_to_update_name}' updated successfully!")
                            st.rerun() # Rerun to reflect changes
                        else:
                            st.error("Could not find the event in the database to update.")
        else:
            st.info("You have no events to update.")

    with tab4:
        st.subheader("See Who's Enrolled in Your Events")
        if not organizer_events_df.empty:
            event_to_view_name = st.selectbox(
                "Select an event to see the candidate list",
                options=organizer_events_df['Seminar_Event_Name'].tolist(),
                index=None,
                placeholder="Choose an event..."
            )
            
            if event_to_view_name:
                try:
                    enrollment_sheet = db_connector.get_worksheet(ENROLLMENT_SHEET_URL, ENROLLMENT_WORKSHEET_NAME)
                    enrollments_df = db_connector.get_dataframe(enrollment_sheet)
                    
                    if not enrollments_df.empty and 'Seminar_Event_Name' in enrollments_df.columns:
                        candidate_list = enrollments_df[enrollments_df['Seminar_Event_Name'] == event_to_view_name]
                        
                        st.write(f"**{len(candidate_list)} candidate(s) enrolled in '{event_to_view_name}':**")
                        if not candidate_list.empty:
                            st.dataframe(candidate_list[['User_FullName']], use_container_width=True)
                        else:
                            st.info("No candidates have enrolled for this event yet.")
                    else:
                        st.warning(f"Could not find enrollment data or required columns in the '{ENROLLMENT_WORKSHEET_NAME}' sheet.")

                except Exception as e:
                    st.error(f"Failed to load enrollment data. Ensure a sheet named '{ENROLLMENT_WORKSHEET_NAME}' exists. Error: {e}")
        else:
            st.info("You have no events to view candidates for.")
