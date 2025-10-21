import streamlit as st
import pandas as pd

# Dummy data
def get_seminars():
    return pd.DataFrame({
        "Title": ["Introduction to AI", "Web Development Basics"],
        "Description": ["A beginner-friendly intro to AI.", "Learn the fundamentals of web dev."],
        "Date": ["2023-10-27", "2023-11-05"],
        "Time": ["15:00", "18:00"],
    })

def user_main():
    st.header("Upcoming Seminars")
    
    seminars_df = get_seminars()
    st.dataframe(seminars_df)

    selected_seminar = st.selectbox("Select a seminar to enroll", seminars_df["Title"])

    st.subheader(f"Enroll in: {selected_seminar}")
    with st.form("enrollment_form"):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        degree = st.text_input("Education - Degree")
        branch = st.text_input("Branch")
        pass_year = st.text_input("Year of Passing")
        experience = st.text_area("Experience")
        about_presenter = st.text_area("Brief about yourself as a presenter (if applicable)")
        linkedin = st.text_input("LinkedIn Profile")
        github = st.text_input("GitHub Profile")
        interests = st.text_area("Area of Interest")

        submitted = st.form_submit_button("Enroll")
        if submitted:
            # Logic to save enrollment details
            st.success(f"You have successfully enrolled in {selected_seminar}!")
            st.info("Your enrollment is pending admin approval.")
