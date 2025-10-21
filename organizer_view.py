import streamlit as st
import pandas as pd
from datetime import datetime

def organizer_main(db_connector):
    """The main function for the Organizer Dashboard page."""
    st.header("📝 Organizer Dashboard")
    st.markdown("Create, manage, and track your seminar events from this dashboard.")

    # --- Define constants for the main Seminar Google Sheet ---
    SEMINAR_SHEET_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
    SEMINAR_WORKSHEET_NAME = "Seminar_Guest_Event_List"

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
        
        # Ensure 'Organizer_Name' column exists for filtering
        if 'Organizer_Name' in seminars_df.columns:
            # Filter events created by the current logged-in user, handling potential empty strings
            organizer_events_df = seminars_df[seminars_df['Organizer_Name'].astype(str) == str(st.session_state.user_name)].copy()
        else:
            # Fallback if the column doesn't exist, show all events with a warning
            organizer_events_df = seminars_df.copy()
            st.sidebar.warning("Sheet is missing 'Organizer_Name' column. Showing all events for now.")

    except Exception as e:
        st.error(f"Failed to load seminar data. Please check the sheet configuration. Error: {e}")
        # Create empty dataframes to prevent crashes in other tabs
        seminars_df = pd.DataFrame()
        organizer_events_df = pd.DataFrame()


    with tab1:
        st.subheader("Create a New Seminar Event")
        with st.form(key="create_seminar_form", clear_on_submit=True):
            st.write("Fill in the details below. This will add your name as the organizer and submit the event for admin approval.")
            
            event_name = st.text_input("Seminar Title *")
            event_date = st.date_input("Date of Event *", min_value=datetime.today())
            domain = st.text_input("Domain / Category *")
            description = st.text_area("Brief Description *")
            meet_link = st.text_input("Google Meet / Session Link")
            evaluation_form_link = st.text_input("Seminar Evaluation Google Form Link")
            
            submit_button = st.form_submit_button(label="Submit for Approval")

            if submit_button:
                if not all([event_name, event_date, domain, description]):
                    st.warning("Please fill in all required fields marked with *.")
                else:
                    # Append the current user's name as the Organizer_Name
                    new_seminar_data = [
                        event_date.strftime("%Y-%m-%d"), # Event_Date
                        event_name,                     # Seminar_Event_Name
                        domain,                         # Domain
                        description,                    # BriefDescription
                        "",                             # URL(Outside)
                        "Not Approved",                 # Approved_Status
                        "Upcoming",                     # Conducted_State
                        "",                             # WhatsappLink
                        meet_link,                      # Meet_session_Link
                        "",                             # Seminar_GuestLecture_Sheet_Link (Presentation)
                        evaluation_form_link,           # Seminar Evaluation-GoogleFormLink
                        "",                             # Sample_Presentation_Links
                        "",                             # Sample_Project_Code_Github_Links
                        "",                             # Sample_Project_Demo_YouTube_Links
                        st.session_state.user_name      # Organizer_Name
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
                            st.rerun()
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
                # Get the specific event's data
                event_data = organizer_events_df[organizer_events_df['Seminar_Event_Name'] == event_to_view_name].iloc[0]
                enrollment_link = event_data.get('Seminar_GuestLecture_Sheet_Link')

                if not enrollment_link or not isinstance(enrollment_link, str) or 'docs.google.com' not in enrollment_link:
                    st.warning("No valid enrollment sheet link found for this seminar. Please add one in the 'Update Your Events' tab.")
                else:
                    try:
                        # Connect to the specific enrollment sheet using its link
                        enrollment_sheet = db_connector.get_worksheet(enrollment_link) # Gets the first tab by default
                        enrollments_df = db_connector.get_dataframe(enrollment_sheet)
                        
                        if 'Presentor_FullName' in enrollments_df.columns:
                            candidate_list = enrollments_df[['Presentor_FullName']].dropna().reset_index(drop=True)
                            
                            st.write(f"**{len(candidate_list)} candidate(s) enrolled in '{event_to_view_name}':**")
                            if not candidate_list.empty:
                                st.dataframe(candidate_list, use_container_width=True)
                            else:
                                st.info("The enrollment sheet is empty.")
                        else:
                            st.error("The linked enrollment sheet is missing the 'Presentor_FullName' column.")

                    except Exception as e:
                        st.error(f"Could not access or read the linked enrollment sheet. Please check the URL and permissions. Error: {e}")
        else:
            st.info("You have no events to view candidates for.")
            
