import streamlit as st
import pandas as pd
from datetime import datetime

def user_main(db_connector):
    """The main function for the User Home page, connected to live Google Sheets."""
    st.header("🏠 User Home")

    # --- Define constants for the Seminar Google Sheet ---
    SEMINAR_SHEET_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
    SEMINAR_WORKSHEET_NAME = "Seminar_Guest_Event_List"

    # --- Fetch Live Seminar Data ---
    try:
        seminar_sheet = db_connector.get_worksheet(SEMINAR_SHEET_URL, SEMINAR_WORKSHEET_NAME)
        seminars_df = db_connector.get_dataframe(seminar_sheet)
        if seminars_df.empty:
            st.info("No seminars are scheduled at the moment.")
            return
    except Exception as e:
        st.error(f"Failed to load seminar data from Google Sheets. Error: {e}")
        return

    # --- Enrollment Logic ---
    # In a real app, this would be a separate lookup from an 'Enrollments' sheet.
    # We'll use session_state to simulate enrollment for the current session.
    if 'enrolled_seminars' not in st.session_state:
        st.session_state.enrolled_seminars = ["Introduction to Machine Learning"] # Pre-enroll in one for demo

    # --- Data Processing ---
    try:
        seminars_df['Event_Date'] = pd.to_datetime(seminars_df['Event_Date'], errors='coerce').dt.date
        seminars_df.dropna(subset=['Event_Date'], inplace=True) # Drop rows where date conversion failed
        today = datetime.now().date()

        # Filter seminars into upcoming and completed
        upcoming_seminars = seminars_df[seminars_df['Event_Date'] >= today].copy()
        completed_seminars = seminars_df[seminars_df['Event_Date'] < today].copy()
    except Exception as e:
        st.error(f"An error occurred while processing seminar dates. Please check the 'Event_Date' column format. Error: {e}")
        return
        
    # --- Create Tabs ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 Upcoming Seminars",
        "✅ My Enrolled Seminars",
        "📝 Seminars to Enroll",
        "📚 Completed Seminars (Peer Learning)"
    ])

    with tab1:
        st.subheader("All Scheduled Future Events")
        display_seminar_list(upcoming_seminars, "View Details")

    with tab2:
        st.subheader("Events You Are Registered For")
        enrolled_df = upcoming_seminars[upcoming_seminars['Seminar_Event_Name'].isin(st.session_state.enrolled_seminars)]
        display_seminar_list(enrolled_df, "Go to Live Session")

    with tab3:
        st.subheader("Available Events You Can Still Join")
        yet_to_enroll_df = upcoming_seminars[~upcoming_seminars['Seminar_Event_Name'].isin(st.session_state.enrolled_seminars)]
        display_seminar_list(yet_to_enroll_df, "Enroll Now")

    with tab4:
        st.subheader("Past Seminars for Review and Learning")
        display_seminar_list(completed_seminars, "Review Session")

def display_seminar_list(seminars_df, button_text):
    """Helper function to display a list of seminars in expanders."""
    if seminars_df.empty:
        st.info("No seminars to display in this category.")
        return

    for index, seminar in seminars_df.iterrows():
        expander_title = f"{seminar.get('Seminar_Event_Name', 'No Title')} - {seminar['Event_Date'].strftime('%B %d, %Y')}"
        with st.expander(expander_title):
            st.markdown(f"**Domain:** {seminar.get('Domain', 'N/A')}")
            st.markdown(f"**Description:** {seminar.get('BriefDescription', 'No description available.')}")
            
            button_key = f"{button_text}_{seminar.get('Seminar_Event_Name', index)}"
            if st.button(button_text, key=button_key):
                # Logic for the "Enroll Now" button
                if button_text == "Enroll Now":
                    seminar_name = seminar['Seminar_Event_Name']
                    if seminar_name not in st.session_state.enrolled_seminars:
                        st.session_state.enrolled_seminars.append(seminar_name)
                        st.success(f"You have successfully enrolled in '{seminar_name}'!")
                        st.rerun() # Rerun to move the seminar to the 'Enrolled' tab
                else:
                    st.session_state.selected_seminar_title = seminar.get('Seminar_Event_Name')
                    st.success(f"Navigating to '{st.session_state.selected_seminar_title}'. Please select 'Live Session' from the sidebar.")



