import streamlit as st
import pandas as pd

def seminar_session_main(db_connector):
    """The main function for the Live Seminar Session page."""
    st.header("🎤 Live Seminar Session")

    # Define constants for Google Sheets
    SEMINAR_SHEET_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
    SEMINAR_WORKSHEET_NAME = "Seminar_Guest_Event_List"

    # --- Fetch Seminar Data ---
    try:
        seminar_sheet = db_connector.get_worksheet(SEMINAR_SHEET_URL, SEMINAR_WORKSHEET_NAME)
        if seminar_sheet:
            seminars_df = db_connector.get_dataframe(seminar_sheet)
        else:
            st.error("Could not connect to the seminar list.")
            seminars_df = pd.DataFrame() # Create empty dataframe on failure
    except Exception as e:
        st.error(f"An error occurred while fetching seminar data: {e}")
        seminars_df = pd.DataFrame()

    # Get the selected seminar title from the session state
    selected_seminar_title = st.session_state.get('selected_seminar_title', None)

    if not selected_seminar_title:
        st.warning("Please select a seminar from the 'User Home' page first to view its details.")
        return

    # Find the details of the selected seminar
    if not seminars_df.empty:
        seminar_details = seminars_df[seminars_df['Seminar_Event_Name'] == selected_seminar_title]
        if not seminar_details.empty:
            seminar_details = seminar_details.iloc[0]
        else:
            st.error(f"Details for '{selected_seminar_title}' could not be found.")
            return
    else:
        st.error("Seminar data is not available.")
        return
    
    st.subheader(f"Now Viewing: {selected_seminar_title}")

    # --- Tabbed Interface ---
    tab1, tab2, tab3 = st.tabs(["▶️ Live Session", "🖼️ Slide View", "❓ Q&A"])

    with tab1:
        st.write("Join the live session using the link below.")
        meet_link = seminar_details.get('Meet_session_Link')
        if meet_link:
            # The st.link_button is a clear and effective way to link to external sites
            st.link_button("🚀 Launch Live Seminar (Opens in New Tab)", meet_link, use_container_width=True)
        else:
            st.info("The Google Meet link for this session has not been provided yet.")

    with tab2:
        st.write("View the presentation slides for this session.")
        slides_link = seminar_details.get('Seminar_GuestLecture_Sheet_Link') # Assuming this column holds the slides link
        
        if slides_link and "docs.google.com/presentation" in slides_link:
            # Construct an embeddable URL for Google Slides
            embed_url = slides_link.replace("/edit", "/embed?start=false&loop=false&delayms=3000")
            st.components.v1.iframe(embed_url, height=480)
        else:
            st.info("The Google Slides link for this session has not been provided or is invalid.")

    with tab3:
        st.subheader("Ask a Question")
        st.write("Submit your questions to the presenter or our AI assistant.")
        
        with st.form("qa_form", clear_on_submit=True):
            slide_number = st.text_input("Relevant Slide Number (if any)")
            question_text = st.text_area("Your Question *")
            ask_target = st.radio("Ask To:", ("Presenter", "AI Assistant (Llama-3)"), horizontal=True)
            
            submit_question = st.form_submit_button("Submit Question")

            if submit_question:
                if not question_text:
                    st.warning("Please enter a question.")
                else:
                    # In a real app, you would save this question to a database
                    st.success(f"Your question has been submitted to the {ask_target}!")
                    st.write(f"**Your Question:** {question_text}")
                    if slide_number:
                        st.write(f"**Regarding Slide:** {slide_number}")
