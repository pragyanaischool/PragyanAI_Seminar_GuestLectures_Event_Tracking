import streamlit as st

def quiz_main():
    st.header("Seminar Quiz")

    st.subheader("In-Presentation Quizzes")
    st.write("Quizzes may appear during the presentation.")
    
    # Placeholder for quiz links
    st.write("Quiz 1: [Link to Quiz]")
    st.write("Quiz 2: [Link to Quiz]")

    st.subheader("Final Quiz")
    st.write("Take the final quiz to test your knowledge.")
    
    with st.form("final_quiz_form"):
        st.write("Question 1: What is the capital of France?")
        q1 = st.radio("Select one:", ('Paris', 'London', 'Berlin', 'Madrid'))

        st.write("Question 2: What is 2 + 2?")
        q2 = st.radio("Select one:", ('3', '4', '5', '6'))
        
        submitted = st.form_submit_button("Submit Quiz")
        if submitted:
            score = 0
            if q1 == 'Paris':
                score += 1
            if q2 == '4':
                score += 1
            
            st.success(f"You scored {score} out of 2.")
