import streamlit as st
import pandas as pd
from datetime import datetime

# --- Caching function for Seminar Data (Already existing) ---
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

# --- Caching function for Presenter/Enrollment Data (Already existing) ---
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
        return pd.DataFrame()
    return pd.DataFrame()

# --- NEW: Caching function for Quiz List Data ---
@st.cache_data(ttl=600)
def get_quiz_list_data(_db_connector, link):
    """Fetches quiz list data from a specific sheet link (Dict_Quizz_List)."""
    try:
        # Assuming the quiz list itself is the entire first sheet/tab of the linked workbook
        spreadsheet = _db_connector.client.open_by_url(link)
        quiz_list_ws = spreadsheet.worksheets()[0] # Use the first worksheet in the linked quiz sheet
        if quiz_list_ws:
            return _db_connector.get_dataframe(quiz_list_ws)
    except Exception as e:
        st.warning(f"Failed to fetch quiz list sheet: {e}")
        return pd.DataFrame()
    return pd.DataFrame()

# --- NEW: Helper function to display slides (reused in tabs)
def display_slides_section(slides_link_from_sheet, manual_slides_link, live_presenter, height=480):
    st.write("View or provide the presentation slides for this session.")
    
    # Use the session link if available, otherwise default to the manual link
    link_to_use = slides_link_from_sheet if slides_link_from_sheet else manual_slides_link

    # Input for manual override
    manual_slides_link_input = st.text_input(
        "Slides URL:", 
        value=link_to_use, 
        placeholder="Paste the Google Slides URL here", 
        key=f"manual_slides_{live_presenter}_{height}"
    )
    
    # Update link_to_use if manual input is provided
    link_to_use = manual_slides_link_input
    
    if link_to_use and "docs.google.com/presentation" in link_to_use:
        # Construct embeddable URL
        embed_url = link_to_use.replace("/edit", "/embed?start=false&loop=false&delayms=3000")
        st.components.v1.iframe(embed_url, height=height)
    else:
        st.info("A valid Google Slides link has not been provided.")


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

        # --- Dynamic Data Retrieval for Tabs ---
        slides_link_from_sheet = ''
        quiz_list_link_from_sheet = ''
        is_quizz_available = 'No' # Default
        
        enrollment_link = live_details.get('Seminar_GuestLecture_Sheet_Link')

        if enrollment_link:
            enrollment_df = get_presenters_data(db_connector, enrollment_link, "Seminar_GuestLecture_List")

            if not enrollment_df.empty:
                presenter_row = enrollment_df[enrollment_df['Presentor_FullName'] == live_presenter]
                if not presenter_row.empty:
                    slides_link_from_sheet = presenter_row.iloc[0].get('PresentationLink', '')
                    quiz_list_link_from_sheet = presenter_row.iloc[0].get('Dict_Quizz_List', '')
                    is_quizz_available = str(presenter_row.iloc[0].get('IsQuizz_During_Session_Available', 'No')).strip()
        
        # Initialize RAG chat history once
        if 'rag_history' not in st.session_state:
            st.session_state.rag_history = []


        # --- Tabbed Interface ---
        tab1, tab2, tab3, tab4 = st.tabs(["▶️ Live Session", "🖼️ Slide View", "❓ Q&A", "🧪 Quizz & RAG"]) # Added 4th tab

        with tab1:
            st.write("Join the live session using the link below.")
            meet_link_from_sheet = live_details.get('Meet_session_Link', '')
            manual_meet_link = st.text_input("Meeting URL:", value=meet_link_from_sheet, placeholder="Paste the meeting URL here if not pre-filled")
            if manual_meet_link:
                st.link_button("🚀 Launch Live Seminar (Opens in New Tab)", manual_meet_link, use_container_width=True)
            else:
                st.info("The meeting link for this session has not been provided.")

        with tab2:
            st.subheader("Presentation Slides")
            st.info("Use this tab for simple slide viewing.")
            display_slides_section(slides_link_from_sheet, None, live_presenter, height=480)

        with tab3:
            st.subheader("Ask a Question")
            st.write("Submit your questions to the Presenter or the AI Assistant.")
            
            # Show chat history if any AI questions have been asked
            if any(role == "AI Assistant" for role, text in st.session_state.rag_history):
                st.markdown("##### 💬 AI Assistant Conversation History")
                # Use a specific key for the history container if needed, or just st.container
                chat_container = st.container(height=200) 
                with chat_container:
                    for role, text in st.session_state.rag_history:
                        if role != "Presenter": # Only display AI chat history here
                            st.markdown(f"**{role}:** {text}")
                            st.markdown("---")
            
            with st.form("qa_form", clear_on_submit=True):
                slide_number = st.text_input("Relevant Slide Number (if any)")
                question_text = st.text_area("Your Question *")
                # Radio button to select target (Presenter or AI)
                ask_target = st.radio("Ask To:", ("Presenter", "AI Assistant (Llama-3)"), horizontal=True)

                submit_question = st.form_submit_button("Submit Question")

                if submit_question:
                    if not question_text:
                        st.warning("Please enter a question.")
                    else:
                        if ask_target == "Presenter":
                            st.success(f"Your question has been submitted to the Presenter!")
                            # In a real app, this would save to a presenter Q&A sheet
                            st.write(f"**Your Question:** {question_text}")
                            if slide_number:
                                st.write(f"**Regarding Slide:** {slide_number}")
                        
                        elif ask_target == "AI Assistant (Llama-3)":
                            # AI Logic: Simulate RAG pipeline and update history
                            st.session_state.rag_history.append(("You", question_text))
                            
                            with st.spinner("AI Assistant is processing... Simulating RAG via GROQ/LangChain..."):
                                
                                # --- Simulated RAG Workflow ---
                                retrieved_content = (
                                    "**Retrieved Snippet (FAISS/PPT Content):** The RAG pipeline uses the **llama-3.3-70b-versatile** model on **GROQ** to run LangChain components "
                                    "(`create_retrieval_chain`, `create_stuff_documents_chain`). This ensures the answer is grounded by the presentation text."
                                )
                                
                                simulated_response = (
                                    f"**AI Response (Simulated):** The AI has processed your query: **'{question_text}'**.\n\n"
                                    f"This demonstrates the RAG process where the AI first retrieves the most relevant context from the embedded presentation content, and then generates an answer.\n\n"
                                    f"***[Context Retrieved]:*** {retrieved_content}\n\n"
                                    f"**[Final Answer]:** Based on the retrieved context, your answer is grounded and verifiable against the slide material."
                                )
                                
                                # Append AI response to history
                                st.session_state.rag_history.append(("AI Assistant", simulated_response))
                                
                                # Clear the input box and rerun to update chat display
                                # Note: Since clear_on_submit=True is set on the form, we only need to rerun.
                                st.rerun()


        with tab4:
            st.subheader("Interactive Quizzing & AI Support (RAG)")
            
            # --- 1. SLIDE DISPLAY (Smaller for context) ---
            st.markdown("##### Presentation Slides (for Context)")
            # Reusing the display logic with smaller height
            display_slides_section(slides_link_from_sheet, None, live_presenter, height=300)
            st.markdown("---")
            
            # --- 2. QUIZ LOGIC ---
            st.markdown("##### 📝 In-Session Quizzes")
            
            if is_quizz_available.upper() == 'YES' and quiz_list_link_from_sheet:
                st.success("Quizzes are available for this session! Test your knowledge.")
                
                quiz_list_df = get_quiz_list_data(db_connector, quiz_list_link_from_sheet) 
                
                if not quiz_list_df.empty:
                    st.markdown("Select a quiz to attempt:")
                    
                    # Assuming the quiz list sheet has columns like 'Quiz No' and 'Quiz Link'
                    for index, row in quiz_list_df.iterrows():
                        quiz_no = row.get('Quiz No', f"Quiz {index+1}")
                        quiz_link = row.get('Quiz Link', '#')
                        
                        if quiz_link and quiz_link != '#':
                            st.link_button(f"Start Quiz: {quiz_no}", quiz_link, key=f"start_quiz_{index}")
                        else:
                            st.warning(f"Link not available for {quiz_no}.")
                            
                    st.caption("Note: Quizzes open in a new tab. After completion, explanations would be displayed here.")
                else:
                    st.warning("Quiz list sheet found, but no quizzes are listed or column headers are incorrect.")
                    
            else:
                st.info("No quizzes are currently available during this session. Check with the organizer.")
            
            # --- RAG/AI LOGIC CLEANUP: Removed duplicate chat input/output logic.
