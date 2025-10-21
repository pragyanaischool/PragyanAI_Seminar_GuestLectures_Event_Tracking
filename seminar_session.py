import streamlit as st
import re

# In a real implementation, you would import your Google Sheets functions
# from google_sheets_db import get_seminar_details 

def get_embed_url_from_google_slides(url: str) -> str:
    """
    Converts a standard Google Slides URL into an embeddable URL for an iframe.
    """
    # Regex to extract the presentation ID from various Google Slides URL formats
    match = re.search(r"/presentation/d/([a-zA-Z0-9-_]+)", url)
    if match:
        presentation_id = match.group(1)
        # Construct the embeddable URL
        return f"https://docs.google.com/presentation/d/{presentation_id}/embed?start=false&loop=false&delayms=3000"
    return None

def seminar_session_main():
    """
    This page hosts the live seminar, providing a link to the Google Meet session,
    presentation slides, and a Q&A section, all organized into tabs.
    It attempts to read data from the database first, otherwise asks the user for input.
    """
    
    # Add logo at the top, consistent with other pages.
    try:
        st.image("PragyanAI_Transperent.png", width=400)
    except Exception as e:
        st.warning("Logo image not found. Please add 'PragyanAI_Transperent.png' to your project directory.")

    st.title("Live Seminar Session")

    # --- Database Simulation ---
    # In a real app, you would fetch the details for the selected seminar from your Google Sheet.
    # For now, we'll simulate this with placeholder variables.
    # seminar_details = get_seminar_details(st.session_state.selected_seminar)
    # db_meet_link = seminar_details.get("meet_link")
    # db_slide_link = seminar_details.get("slide_link")
    
    # Simulating that no links were found in the database initially.
    # To test the "found in database" path, change these to a URL string.
    db_meet_link = None 
    db_slide_link = "https://docs.google.com/presentation/d/1Pw-yvOblXeGqAKtJ8smB__JuWQNG7N_P/edit?usp=sharing&ouid=107026895892172547790&rtpof=true&sd=true"

    st.markdown("---")

    # --- Tabbed Layout for the Session ---
    tab_live, tab_slides, tab_qa = st.tabs(["▶️ Live Session", "🖼️ Slide View", "❓ Q&A"])

    with tab_live:
        st.header("Join the Live Google Meet Session")
        
        meet_link = db_meet_link
        # If the link wasn't found in the database, ask the user for it.
        if not meet_link:
            st.warning("No meeting link found for this seminar.")
            meet_link = st.text_input("Please paste the Google Meet Link for the Session here:")

        if meet_link:
            st.info("Click the button below to launch the live seminar in a new browser tab for the full experience.")
            st.markdown(
                f"""
                <a href="{meet_link}" target="_blank" style="text-decoration: none;">
                    <div style="
                        display: inline-block; padding: 1em 2em; margin-top: 1em;
                        background-color: #D93025; color: white; border-radius: 8px;
                        font-size: 22px; font-weight: bold; text-align: center;
                    ">
                        🚀 Launch Live Seminar
                    </div>
                </a>
                """,
                unsafe_allow_html=True
            )
        else:
            st.error("A Google Meet link is required to start the session.")

    with tab_slides:
        st.header("Presentation Slides")
        
        slide_link = db_slide_link
        # If the link wasn't found in the database, ask the user for it.
        if not slide_link:
            st.warning("No presentation link found for this seminar.")
            slide_link = st.text_input("Please paste the Google Slides share link here:")
        
        if slide_link:
            embed_url = get_embed_url_from_google_slides(slide_link)
            if embed_url:
                st.info("The presentation is embedded below. You can also open it in a new tab.")
                st.components.v1.iframe(embed_url, height=500, scrolling=True)
                st.markdown(f'<a href="{slide_link}" target="_blank">Open Slides in New Tab</a>', unsafe_allow_html=True)
            else:
                st.error("Invalid Google Slides link. Please make sure you have pasted the correct share URL.")
        else:
            st.error("A Google Slides link is required to view the presentation.")

    with tab_qa:
        st.header("Ask a Question")
        st.info("Have a question? Fill out the details below.")

        # Q&A Form
        with st.form("qa_form"):
            slide_number = st.number_input("Regarding Slide Number:", min_value=1, step=1)
            question_target = st.radio("Ask your question to:", ("Presenter", "AI Assistant"), horizontal=True)
            question_text = st.text_area("Your Question:")
            submitted = st.form_submit_button("Submit Question")
            
            if submitted:
                if question_text:
                    st.success(f"Your question for the **{question_target}** regarding slide **#{slide_number}** has been submitted!")
                else:
                    st.error("Please type a question before submitting.")

