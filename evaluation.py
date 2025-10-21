import streamlit as st

def evaluation_main(db_connector):
    """The main function for the Seminar Evaluation page."""
    st.title("📝 Seminar Evaluation")
    st.info("This page allows you to provide feedback on the seminars you have attended.")
    st.divider()

    selected_seminar = st.session_state.get('selected_seminar_title', None)

    if not selected_seminar:
        st.warning("To leave feedback, please first select a seminar from the '🏠 User Home' page.")
        return

    st.header(f"Evaluating: \"{selected_seminar}\"")
    st.write("Please rate the following aspects of the seminar on a scale of 1 to 5.")

    with st.form("evaluation_form"):
        # Sliders for ratings
        presentation_quality = st.slider("Presentation Quality (Clarity, Slides, etc.)", 1, 5, 3, help="How clear and visually appealing was the presentation?")
        presentation_skill = st.slider("Presenter's Skill (Engagement, Pace, etc.)", 1, 5, 3, help="How engaging and well-paced was the speaker?")
        content_info = st.slider("Content & Information (Depth, Relevance, Research)", 1, 5, 3, help="How informative and relevant was the content?")
        knowledge_depth = st.slider("Knowledge Depth of Presenter", 1, 5, 3, help="How well did the presenter know the subject matter?")
        
        # Text area for qualitative feedback
        learnings = st.text_area("What are your key takeaways or learnings from this session?")
        
        # Overall rating
        overall_rating = st.select_slider(
            "Overall Rating",
            options=['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'],
            value='Good'
        )

        submitted = st.form_submit_button("Submit Feedback", use_container_width=True)
        if submitted:
            # In a real application, this data would be saved to a Google Sheet or another database.
            st.success("Thank you for your feedback! It has been submitted successfully.")

