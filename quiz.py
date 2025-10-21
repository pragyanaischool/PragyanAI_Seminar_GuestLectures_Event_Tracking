import streamlit as st

def quiz_main(db_connector):
    """The main function for the Quiz page."""
    st.title("🧠 Seminar Quiz")
    st.info("Test your knowledge on the topics covered in the seminar.")
    st.divider()

    selected_seminar = st.session_state.get('selected_seminar_title', None)

    if not selected_seminar:
        st.warning("To take a quiz, please first select a seminar from the '🏠 User Home' page.")
        return

    st.header(f"Quiz for: \"{selected_seminar}\"")
    
    # This is a placeholder for the quiz logic.
    # In a real app, you would fetch quiz questions from a Google Sheet or another database
    # based on the selected_seminar.

    st.subheader("Quiz Questions")

    # --- Dummy Quiz Questions ---
    questions = [
        {
            "question": "What is the primary goal of supervised learning?",
            "options": ["To find hidden patterns in data", "To make predictions based on labeled data", "To group similar data points together", "To learn from unlabeled data"],
            "answer": "To make predictions based on labeled data"
        },
        {
            "question": "Which of the following is NOT a core component of React?",
            "options": ["Components", "State", "Props", "Directives"],
            "answer": "Directives"
        },
        {
            "question": "What does the 'Q' in quantum computing stand for?",
            "options": ["Quality", "Qubit", "Quantum", "Query"],
            "answer": "Quantum"
        }
    ]

    user_answers = {}
    for i, q in enumerate(questions):
        user_answers[f"q_{i}"] = st.radio(q["question"], q["options"], key=f"q_{i}")

    if st.button("Submit Answers", use_container_width=True, type="primary"):
        score = 0
        for i, q in enumerate(questions):
            if user_answers[f"q_{i}"] == q["answer"]:
                score += 1
        
        st.success(f"Quiz Submitted! Your score is {score} out of {len(questions)}.")
        st.balloons()

