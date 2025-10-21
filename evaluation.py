import streamlit as st

def evaluation_main():
    st.header("Seminar Evaluation")

    with st.form("evaluation_form"):
        st.subheader("Please rate the following:")
        
        presentation_quality = st.slider("Presentation Quality", 1, 5, 3)
        presentation_skill = st.slider("Presentation Skill", 1, 5, 3)
        content_information = st.slider("Content - Information - Research", 1, 5, 3)
        knowledge_depth = st.slider("Knowledge Depth of Presenter", 1, 5, 3)
        
        st.subheader("Your Learnings")
        topics_learned = st.text_area("What are the key topics you learned?")
        
        st.subheader("Overall Rating")
        overall_rating = st.slider("Overall Rating", 1, 5, 3)

        st.subheader("Voice Feedback (Recording)")
        st.info("Voice recording feature would be implemented here.")
        # Placeholder for voice recording functionality

        submitted = st.form_submit_button("Submit Evaluation")
        if submitted:
            st.success("Thank you for your feedback!")
