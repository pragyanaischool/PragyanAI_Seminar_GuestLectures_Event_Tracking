import streamlit as st
import pandas as pd
from datetime import datetime

def organizer_main(db_connector):
    """The main function for the Organizer Dashboard page."""
    st.header("📝 Organizer Dashboard")
    st.markdown("Create and manage your seminar events from this dashboard.")

    # --- Define constants for the Seminar Google Sheet ---
    SEMINAR_SHEET_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
    SEMINAR_WORKSHEET_NAME = "Seminar_Guest_Event_List"

    # --- Create a New Seminar Event Form ---
    st.subheader("Create a New Seminar Event")
    
    with st.form(key="create_seminar_form", clear_on_submit=True):
        st.write("Fill in the details below to schedule a new seminar. It will be sent to an admin for approval.")
        
        # Get event details from user
        event_name = st.text_input("Seminar Title *")
        event_date = st.date_input("Date of Event *", min_value=datetime.today())
        domain = st.text_input("Domain / Category (e.g., AI/ML, Web Development) *")
        description = st.text_area("Brief Description *")
        meet_link = st.text_input("Google Meet / Session Link")
        presentation_link = st.text_input("Google Slides / Presentation Link")
        
        submit_button = st.form_submit_button(label="Submit for Approval")

        if submit_button:
            # --- Form Validation ---
            if not all([event_name, event_date, domain, description]):
                st.warning("Please fill in all required fields marked with *.")
            else:
                try:
                    seminar_sheet = db_connector.get_worksheet(SEMINAR_SHEET_URL, SEMINAR_WORKSHEET_NAME)
                    
                    # Prepare the new row data
                    new_seminar_data = [
                        event_date.strftime("%Y-%m-%d"),
                        event_name,
                        domain,
                        description,
                        "", # URL(Outside) - Leave blank
                        "Not Approved", # Approved_Status
                        "Upcoming", # Conducted_State
                        "", # WhatsappLink - Admin to fill
                        meet_link,
                        presentation_link,
                        "", # Seminar Evaluation-GoogleFormLink
                        "", # Sample_Presentation_Links
                        "", # Sample_Project_Code_Github_Links
                        ""  # Sample_Project_Demo_YouTube_Links
                    ]
                    
                    db_connector.append_record(seminar_sheet, new_seminar_data)
                    st.success(f"Successfully submitted '{event_name}' for approval!")

                except Exception as e:
                    st.error(f"An error occurred while creating the event: {e}")

    # --- Display Existing Seminars (Optional) ---
    st.subheader("Your Submitted Events")
    try:
        seminar_sheet = db_connector.get_worksheet(SEMINAR_SHEET_URL, SEMINAR_WORKSHEET_NAME)
        seminars_df = db_connector.get_dataframe(seminar_sheet)
        if not seminars_df.empty:
            # A real app would filter by the organizer's name. For now, we show all.
            st.dataframe(seminars_df[['Seminar_Event_Name', 'Event_Date', 'Domain', 'Approved_Status']], use_container_width=True)
        else:
            st.info("You have not submitted any events yet.")
    except Exception as e:
        st.error(f"Failed to load existing seminar data. Error: {e}")


