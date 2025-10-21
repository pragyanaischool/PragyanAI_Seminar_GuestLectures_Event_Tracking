import streamlit as st
import pandas as pd
from datetime import datetime

def seminar_session_main(db_connector):
    """The main function for the Live Seminar Session page."""
    st.header("🎤 Go to a Live Session")

    # --- Add a refresh button ---
    if st.button("🔄 Refresh Events List"):
        # Clear session state related to the session view to reset the page
        st.session_state.pop('show_live_session', None)
        st.session_state.pop('live_session_details', None)
        st.session_state.pop('live_session_presenter', None)
        st.rerun()

    # Define constants for Google Sheets
    SEMINAR_SHEET_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
    SEMINAR_WORKSHEET_NAME = "Seminar_Guest_Event_List"

    # --- Fetch and Filter Seminar Data ---
    try:
        seminar_sheet = db_connector.get_worksheet(SEMINAR_SHEET_URL, SEMINAR_WORKSHEET_NAME)
        if seminar_sheet:
            seminars_df = db_connector.get_dataframe(seminar_sheet)
            seminars_df['Event_Date'] = pd.to_datetime(seminars_df['Event_Date'], errors='coerce')
            today = pd.to_datetime(datetime.now().date())
            upcoming_seminars_df = seminars_df[seminars_df['Event_Date'] >= today].copy()
            upcoming_seminars_df.sort_values(by='Event_Date', inplace=True)
        else:
            st.error("Could not connect to the seminar list.")
            upcoming_seminars_df = pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred while fetching seminar data: {e}")
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
                try:
                    enrollment_ws = db_connector.get_worksheet(enrollment_sheet_link, "Seminar_GuestLecture_List")
                    if enrollment_ws:
                        presenters_df = db_connector.get_dataframe(enrollment_ws)
                except Exception:
                    st.warning("Could not fetch presenter list for this event.")

        selected_presenter = None
        if seminar_details is not None and not presenters_df.empty:
            st.subheader("Step 2: Select a Presenter")
            presenter_options = presenters_df['Presentor_FullName'].tolist() if 'Presentor_FullName' in presenters_df.columns else []
            selected_presenter = st.selectbox("Choose a presenter:", options=["-- Select a Presenter --"] + presenter_options)

        if selected_presenter and selected_presenter != "-- Select a Presenter --":
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
            if enrollment_link:
                # --- ADDED FOR DEBUGGING ---
                st.info(f"Debugging: Looking for slides in this sheet: {enrollment_link}")
                try:
                    enrollment_ws = db_connector.get_worksheet(enrollment_link, "Seminar_GuestLecture_List")
                    st.info(f"Debugging: enrollment_ws: {enrollment_ws}")
                    if enrollment_ws:
                        enrollment_df = db_connector.get_dataframe(enrollment_ws)
                        st.write(enrollment_df.head())
                        presenter_row = enrollment_df[enrollment_df['Presentor_FullName'] == live_presenter]
                        st.write(live_presenter, enrollment_df['Presentor_FullName'] )
                        st.info(presenter_row)
                        if not presenter_row.empty:
                            for i in range(len(presenter_row)):
                                slides_link_from_sheet = presenter_row.iloc[i].get('PresentationLink', '')
                                st.write(slides_link_from_sheet )
                except Exception:
                    st.warning("Could not automatically retrieve the presentation link.")

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
