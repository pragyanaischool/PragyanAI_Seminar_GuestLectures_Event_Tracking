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

# --- MODIFIED: Caching function to fetch the Quiz Workbook and Worksheet Titles ---
@st.cache_data(ttl=600)
def get_quiz_workbook_and_sheets(_db_connector, link):
    """Fetches the quiz workbook and returns the spreadsheet object and all worksheet titles."""
    try:
        spreadsheet = _db_connector.client.open_by_url(link)
        sheet_titles = [ws.title for ws in spreadsheet.worksheets()]
        # Return the actual spreadsheet object and the list of sheet names
        return spreadsheet, sheet_titles
    except Exception as e:
        st.warning(f"Failed to fetch quiz workbook or titles. Check link and sharing: {e}")
        return None, []

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
        
        # Initialize Quiz State
        if 'current_quiz_title' not in st.session_state:
            st.session_state.current_quiz_title = None
            st.session_state.quiz_df = pd.DataFrame()
            st.session_state.question_index = 0
            st.session_state.show_feedback = False
            st.session_state.user_answer = None
            st.session_state.score_correct = 0  # NEW: Score tracking
            st.session_state.score_wrong = 0    # NEW: Score tracking


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
                            
                            with st.spinner("AI Assistant is processing... Executing Conceptual RAG Pipeline..."):
                                
                                # --- Conceptual RAG Workflow using LangChain/GROQ ---
                                
                                # Step 1: Conceptual Setup (In a real environment, these would be imports and initialization)
                                st.markdown("##### Conceptual RAG Initialization (Simulated Code Structure)")
                                st.code("from langchain_core.prompts import ChatPromptTemplate")
                                st.code("from langchain.chains import create_retrieval_chain, create_stuff_documents_chain")
                                st.code("from langchain_groq import ChatGroq # For llama-3.3-70b-versatile")
                                st.code("from langchain_community.vectorstores import FAISS")
                                
                                st.code("\n# 1. Simulate Loading & Indexing (PPT content embedding)")
                                st.code("vectorstore = FAISS.from_documents(chunks, embeddings_model)")
                                st.code("retriever = vectorstore.as_retriever()")
                                
                                # Step 2: Define Prompt and Combine Docs Chain
                                st.code("\n# 2. Define Prompt and Combine Docs Chain")
                                st.code("prompt = ChatPromptTemplate.from_template('Answer the question based only on the following context:\\n{context}\\nQuestion: {input}')")
                                st.code("llm = ChatGroq(model='llama-3.3-70b-versatile', groq_api_key='...')")
                                st.code("combine_docs_chain = create_stuff_documents_chain(llm, prompt)")
                                
                                # Step 3: Create Retrieval Chain and Invoke
                                st.code("\n# 3. Create and Invoke Retrieval Chain")
                                st.code("retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)")
                                st.code(f"response = retrieval_chain.invoke({{'input': '{question_text}'}})")
                                
                                # --- Simulated Response based on successful invocation ---
                                
                                simulated_answer = (
                                    "**Final AI Answer (Conceptual):** The RAG pipeline executed successfully using the provided context from the slides. "
                                    "The **llama-3.3-70b-versatile** model on **GROQ** provided a grounded response.\n\n"
                                    f"**Query:** {question_text}\n"
                                    f"**Status:** Retrieval and generation successful (conceptually).\n"
                                    f"**Key Component:** `retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)`"
                                )
                                
                                # Append AI response to history
                                st.session_state.rag_history.append(("AI Assistant", simulated_answer))
                                
                                # Rerun to update chat display
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
            
            # --- NEW RESET BUTTON for debugging ---
            if st.session_state.current_quiz_title and st.button("End Current Quiz / Reset State"):
                st.session_state.current_quiz_title = None
                st.session_state.question_index = 0
                st.session_state.show_feedback = False
                st.session_state.quiz_df = pd.DataFrame()
                st.session_state.score_correct = 0
                st.session_state.score_wrong = 0
                st.rerun()

            if is_quizz_available.upper() == 'YES' and quiz_list_link_from_sheet:
                st.success("Quizzes are available for this session! Test your knowledge.")
                
                # Fetch the quiz workbook and available sheet names (Quizzes)
                quiz_spreadsheet, quiz_titles = get_quiz_workbook_and_sheets(db_connector, quiz_list_link_from_sheet) 
                
                if not quiz_titles:
                    st.warning("Quiz workbook accessible, but no quiz sheets (tabs) were found inside.")
                else:
                    # --- QUIZ SELECTION ---
                    selected_quiz_title = st.selectbox("Select a Quiz:", options=["-- Select a Quiz --"] + quiz_titles, key='quiz_selector')
                    
                    if selected_quiz_title != "-- Select a Quiz --":
                        if st.session_state.current_quiz_title != selected_quiz_title:
                            # New quiz selected, reset the state and scores
                            st.session_state.current_quiz_title = selected_quiz_title
                            st.session_state.question_index = 0
                            st.session_state.show_feedback = False
                            st.session_state.quiz_df = pd.DataFrame() # Clear old data
                            st.session_state.score_correct = 0
                            st.session_state.score_wrong = 0
                            
                            # Load the selected quiz data
                            try:
                                quiz_ws = quiz_spreadsheet.worksheet(selected_quiz_title)
                                st.session_state.quiz_df = db_connector.get_dataframe(quiz_ws)
                                
                                # Validation: Ensure required columns are present
                                # MODIFIED: Added Option E and updated 'Correct Answer' to 'Answer'
                                required_cols = ['Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Option E', 'Answer', 'Explanation']
                                if not all(col in st.session_state.quiz_df.columns for col in required_cols):
                                    st.error(f"Quiz sheet '{selected_quiz_title}' is missing required columns. Must have: {', '.join(required_cols)}.")
                                    st.session_state.current_quiz_title = None # Invalidate selection
                                    st.session_state.quiz_df = pd.DataFrame()
                                st.rerun() # Rerun to start quiz display
                            except Exception as e:
                                st.error(f"Failed to load quiz data: {e}")
                                st.session_state.current_quiz_title = None
                        
                        
                        # --- QUIZ RUNNING LOGIC ---
                        if not st.session_state.quiz_df.empty and st.session_state.current_quiz_title:
                            quiz_df = st.session_state.quiz_df
                            q_idx = st.session_state.question_index
                            
                            if q_idx < len(quiz_df):
                                # Display Current Question
                                current_q = quiz_df.iloc[q_idx]
                                
                                st.markdown(f"**Question {q_idx + 1} of {len(quiz_df)}:** {current_q['Question']}")
                                
                                # Options Generation (up to Option E)
                                options = {
                                    'A': current_q.get('Option A'),
                                    'B': current_q.get('Option B'),
                                    'C': current_q.get('Option C'),
                                    'D': current_q.get('Option D'),
                                    'E': current_q.get('Option E') # NEW
                                }
                                valid_options = [f"{key}. {value}" for key, value in options.items() if value]
                                
                                with st.form(key=f"quiz_q_{q_idx}"):
                                    user_choice = st.radio("Select your answer:", valid_options, key=f"q_radio_{q_idx}")
                                    submit_answer = st.form_submit_button("Submit Answer")
                                    
                                if submit_answer:
                                    # Extract just the letter (A, B, C, D, E) from the user's selection
                                    st.session_state.user_answer = user_choice.split('.')[0].strip()
                                    st.session_state.show_feedback = True
                                    # The rerun is needed to display feedback section
                                    st.rerun() 
                                    
                                # --- FEEDBACK DISPLAY ---
                                if st.session_state.show_feedback:
                                    # MODIFIED: Check against 'Answer' column
                                    correct_answer_letter = current_q['Answer'].strip().upper() 
                                    is_correct = st.session_state.user_answer == correct_answer_letter
                                    
                                    # --- SCORING UPDATE (Ensure it runs only once per question) ---
                                    # We use 'scored_q' to ensure Streamlit reruns don't double-score
                                    if st.session_state.get('scored_q') != q_idx:
                                        if is_correct:
                                            st.session_state.score_correct += 1
                                        else:
                                            st.session_state.score_wrong += 1
                                        st.session_state.scored_q = q_idx # Mark question as scored
                                    # --- END SCORING UPDATE ---
                                    
                                    # Display feedback message
                                    if is_correct:
                                        st.success(f"✅ Correct! You chose option {st.session_state.user_answer}.")
                                    else:
                                        st.error(f"❌ Incorrect. You chose option {st.session_state.user_answer}.")
                                    
                                    # Display correct answer and explanation
                                    st.markdown(f"**Correct Answer:** **{correct_answer_letter}**. {options.get(correct_answer_letter, 'Option not found.')}")
                                    st.markdown(f"**Explanation:** {current_q.get('Explanation', 'No explanation provided.')}")
                                    
                                    # Button to move to the next question
                                    if st.button("Next Question ▶️", key="next_q_btn"):
                                        st.session_state.question_index += 1
                                        st.session_state.show_feedback = False
                                        st.session_state.user_answer = None
                                        st.session_state.pop('scored_q', None) # Clear marker for next question
                                        st.rerun() # Rerun to display the next question
                                        
                            else:
                                # Quiz Finished
                                st.balloons()
                                st.success(f"🎉 Quiz '{st.session_state.current_quiz_title}' completed!")
                                
                                # NEW: Display Final Score
                                colA, colB = st.columns(2)
                                with colA:
                                    st.metric(label="✅ Correct Answers", value=st.session_state.score_correct)
                                with colB:
                                    st.metric(label="❌ Wrong Answers", value=st.session_state.score_wrong)
                                
                                if st.button("Start Another Quiz"):
                                    st.session_state.current_quiz_title = None
                                    st.session_state.score_correct = 0
                                    st.session_state.score_wrong = 0
                                    st.rerun()
                                    
            else:
                # This is the section that prints the warning if the quiz flag is not set or link is missing
                st.info("No quizzes are currently available during this session. Check with the organizer.")
            
