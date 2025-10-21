import streamlit as st

def organizer_main():
    st.header("Create a New Seminar")

    with st.form("seminar_form"):
        seminar_title = st.text_input("Seminar Title")
        seminar_description = st.text_area("Seminar Description")
        seminar_date = st.date_input("Date")
        seminar_time = st.time_input("Time")
        meet_link = st.text_input("Google Meet/Other Link")
        
        submitted = st.form_submit_button("Create Seminar")
        if submitted:
            # In a real app, you'd save this data
            st.success(f"Seminar '{seminar_title}' created successfully!")
