import streamlit as st
import pandas as pd
from datetime import datetime

# --- NEW: Caching function for Seminar Data ---
@st.cache_data(ttl=600)  # Cache the data for 10 minutes (600 seconds)
def get_seminar_data(_db_connector, url, name):
    """Fetches and processes seminar data, caching the result."""
    # Note: _db_connector is intentionally prefixed with '_' so Streamlit doesn't try to hash the object
    seminar_sheet = _db_connector.get_worksheet(url, name)
    if seminar_sheet:
        seminars_df = _db_connector.get_dataframe(seminar_sheet)
        # Ensure date column is correct type before filtering
        seminars_df['Event_Date'] = pd.to_datetime(seminars_df['Event_Date'], errors='coerce')
        today = pd.to_datetime(datetime.now().date())
        upcoming_seminars_df = seminars_df[seminars_df['Event_Date'] >= today].copy()
        upcoming_seminars_df.sort_values(by='Event_Date', inplace=True)
        return upcoming_seminars_df
    return pd.DataFrame()

# --- NEW: Caching function for Presenter/Enrollment Data ---
@st.cache_data(ttl=600)  # Cache enrollment data for 10 minutes
def get_presenters_data(_db_connector, link, worksheet_name):
    """Fetches presenter data from a specific enrollment link."""
    # Note: _db_connector is intentionally prefixed with '_'
    try:
        enrollment_ws = _db_connector.get_worksheet(link, worksheet_name)
        if enrollment_ws:
            return _db_connector.get_dataframe(enrollment_ws)
    except Exception as e:
        # Returning an empty DataFrame here is safer than raising an exception
        # st.warning(f"Error fetching presenter data for link: {e}") 
        return pd.DataFrame()
    return pd.DataFrame()

def seminar_session_main(db_connector):
    """The main function for the Live Seminar Session page."""
    st.header("🎤 Go to a Live Session")

    # --- Add a refresh button ---
    if st.button("🔄 Refresh Events List"):
        # Clear session state related to the session view to reset the page
        st.session_state.pop('show_live_session', None)
        st.session_state.pop('live_session_details', None)
        st.session_state.pop('live_session_presenter', None)
        
        # Invalidate the cached data to force a fresh API call
        get_seminar_data.clear()
        get_presenters_data.clear()
        
        st.rerun()

    # Define constants for Google Sheets
    SEMINAR_SHEET_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
    SEMINAR_WORKSHEET_NAME = "Seminar_Guest_Event_List"

    # --- Fetch and Filter Seminar Data (Now uses cached function) ---
    try:
        # Pass db_connector as the non-hashed argument
        upcoming_seminars_df = get_seminar_data(db_connector, SEMINAR_SHEET_URL, SEMINAR_WORKSHEET_NAME)
    except Exception as e:
        st.error(f"An error occurred while fetching seminar data: {e}. Check your connection.")
        upcoming_seminars_df = pd.DataFrame()

    # --- Selection Logic (only show if not in a live session view) ---
    if not st.session_state.get('show_live_session', False):
        if upcoming_seminars_df.empty:
            st.info("There are no current or upcoming seminar events.")
            return

        st.subheader("Step 1: Select a Seminar")
        event_options = upcoming_seminars_df['Seminar_Event_Name'].tolist()
        selected_event_name = st.selectbox("Choose an event:", options=["-- Select an Event --"] + event_options)

        seminar_details = None
        presenters_df = pd.DataFrame()

        if selected_event_name != "-- Select an Event --":
            seminar_details = upcoming_seminars_df[upcoming_seminars_df['Seminar_Event_Name'] == selected_event_name].iloc[0]
            enrollment_sheet_link = seminar_details.get('Seminar_GuestLecture_Sheet_Link')
            if enrollment_sheet_link:
                # --- Get presenter data using cached function ---
                # Pass db_connector as the non-hashed argument
                presenters_df = get_presenters_data(db_connector, enrollment_sheet_link, "Seminar_GuestLecture_List")
                
                if presenters_df.empty:
                     st.warning("Could not fetch presenter list for this event.")


        selected_presenter = None
        if seminar_details is not None and not presenters_df.empty:
            st.subheader("Step 2: Select a Presenter")
            presenter_options = presenters_df['Presentor_FullName'].tolist() if 'Presentor_FullName' in presenters_df.columns else []
            selected_presenter = st.selectbox("Choose a presenter:", options=["-- Select a Presenter --"] + presenter_options)

        if selected_presenter and selected_presenter != "-- Select an Event --":
            if st.button("🚀 Go to Live Session", use_container_width=True, type="primary"):
                st.session_state['show_live_session'] = True
                st.session_state['live_session_details'] = seminar_details.to_dict()
                st.session_state['live_session_presenter'] = selected_presenter # Store the selected presenter
                st.rerun()
    
    # --- Display the Live Session View if triggered ---
    if st.session_state.get('show_live_session', False):
        live_details = st.session_state.get('live_session_details', {})
        live_presenter = st.session_state.get('live_session_presenter', '')
        
        st.success(f"Now Viewing: {live_details.get('Seminar_Event_Name')} with {live_presenter}")

        if st.button("🔄 Refresh Session Info"):
            # Clear data cache and rerun to get fresh info on demand
            get_presenters_data.clear() 
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["▶️ Live Session", "🖼️ Slide View", "❓ Q&A"])

        with tab1:
            st.write("Join the live session using the link below.")
            meet_link_from_sheet = live_details.get('Meet_session_Link', '')
            manual_meet_link = st.text_input("Meeting URL:", value=meet_link_from_sheet, placeholder="Paste the meeting URL here if not pre-filled")
            if manual_meet_link:
                st.link_button("🚀 Launch Live Seminar (Opens in New Tab)", manual_meet_link, use_container_width=True)
            else:
                st.info("The meeting link for this session has not been provided.")

        with tab2:
            st.write("View or provide the presentation slides for this session.")
            
            slides_link_from_sheet = ''
            enrollment_link = live_details.get('Seminar_GuestLecture_Sheet_Link')
            
            # Use cached function here as well
            if enrollment_link:
                st.info(f"Debugging: Looking for slides in this sheet: {enrollment_link}")
                # Pass db_connector as the non-hashed argument
                enrollment_df = get_presenters_data(db_connector, enrollment_link, "Seminar_GuestLecture_List")

                if not enrollment_df.empty:
                    presenter_row = enrollment_df[enrollment_df['Presentor_FullName'] == live_presenter]
                    if not presenter_row.empty:
                        slides_link_from_sheet = presenter_row.iloc[0].get('PresentationLink', '')
                else:
                    st.warning("Could not automatically retrieve the presentation link from the enrollment sheet.")

            manual_slides_link = st.text_input("Slides URL:", value=slides_link_from_sheet, placeholder="Paste the Google Slides URL here")
            if manual_slides_link and "docs.google.com/presentation" in manual_slides_link:
                embed_url = manual_slides_link.replace("/edit", "/embed?start=false&loop=false&delayms=3000")
                st.components.v1.iframe(embed_url, height=480)
            else:
                st.info("A valid Google Slides link has not been provided.")
        
        with tab3:
            st.subheader("Ask a Question")
            with st.form("qa_form", clear_on_submit=True):
                slide_number = st.text_input("Relevant Slide Number (if any)")
                question_text = st.text_area("Your Question *")
                ask_target = st.radio("Ask To:", ("Presenter", "AI Assistant (Llama-3)"), horizontal=True)
                submit_question = st.form_submit_button("Submit Question")
                if submit_question and question_text:
                    st.success(f"Your question has been submitted to the {ask_target}!")
                elif submit_question:
                    st.warning("Please enter a question.")
                    
