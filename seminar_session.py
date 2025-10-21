import streamlit as st

def seminar_session_main():
    """
    This page hosts the live seminar, providing a link to the Google Meet session,
    presentation slides, and a Q&A section, all organized into tabs.
    """
    
    # Add logo at the top, consistent with other pages.
    try:
        st.image("PragyanAI_Transperent.png", width=400)
    except Exception as e:
        st.warning("Logo image not found. Please add 'PragyanAI_Transperent.png' to your project directory.")

    st.title("Live Seminar Session")

    # --- URL Input for the Live Session ---
    # In a real app, this would be loaded from your seminar database.
    meet_link = st.text_input(
        "Paste the Google Meet Link for the Session here:", 
        "https://meet.google.com/aim-ymsn-daw" # Default example
    )

    st.markdown("---")

    # --- Tabbed Layout for the Session ---
    tab_live, tab_slides, tab_qa = st.tabs(["▶️ Live Session", "🖼️ Slide View", "❓ Q&A"])

    with tab_live:
        st.header("Join the Live Google Meet Session")
        if meet_link:
            st.info("Click the button below to launch the live seminar in a new browser tab for the full experience.")
            
            # Use the URL to create a launch button
            st.markdown(
                f"""
                <a href="{meet_link}" target="_blank" style="text-decoration: none;">
                    <div style="
                        display: inline-block;
                        padding: 1em 2em;
                        margin-top: 1em;
                        background-color: #D93025; /* Google Meet Red */
                        color: white;
                        border-radius: 8px;
                        font-size: 22px;
                        font-weight: bold;
                        text-align: center;
                    ">
                        🚀 Launch Live Seminar
                    </div>
                </a>
                """,
                unsafe_allow_html=True
            )
            with st.expander("Why doesn't the video appear on this page?"):
                st.warning(
                    """
                    **Technical Note:** For security and privacy reasons, Google Meet does not allow its video calls to be embedded directly into other websites. The most secure and reliable method is to open the meeting in its own browser tab.
                    """
                )
        else:
            st.warning("Please paste a Google Meet link above to activate the launch button.")

    with tab_slides:
        st.header("Presentation Slides")
        st.info("The presenter's slides will appear here. Use the buttons to navigate.")
        
        # Placeholder for slide navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.button("⬅️ Previous Slide")
        with col3:
            st.button("Next Slide ➡️")
            
        # Placeholder for the slide image
        st.image("https://placehold.co/800x450/EEE/31343C?text=Slide+Content+Area", use_column_width=True)

    with tab_qa:
        st.header("Ask a Question")
        st.info("Have a question? Fill out the details below.")

        # Q&A Form
        with st.form("qa_form"):
            slide_number = st.number_input("Regarding Slide Number:", min_value=1, step=1)
            
            question_target = st.radio(
                "Ask your question to:",
                ("Presenter", "AI Assistant"),
                horizontal=True
            )
            
            question_text = st.text_area("Your Question:")
            
            submitted = st.form_submit_button("Submit Question")
            
            if submitted:
                if question_text:
                    st.success(f"Your question for the **{question_target}** regarding slide **#{slide_number}** has been submitted!")
                    # Here you would add logic to send the question to the presenter or the Groq Llama3.1 API
                else:
                    st.error("Please type a question before submitting.")

