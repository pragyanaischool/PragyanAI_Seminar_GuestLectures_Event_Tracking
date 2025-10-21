import streamlit as st
import pandas as pd
from dummy_data import get_dummy_seminars
from datetime import datetime

def user_main(db_connector):
    """The main function for the User Home page."""
    st.header("🏠 User Home")

    # In a real app, you'd get this from the database based on the logged-in user.
    # For dummy mode, we'll create a sample list.
    dummy_enrolled_seminars = ["Introduction to Machine Learning", "Advanced Python for Developers"]

    # Load seminar data
    seminars_df = get_dummy_seminars()
    # Ensure 'Event_Date' is a datetime object for comparison
    seminars_df['Event_Date'] = pd.to_datetime(seminars_df['Event_Date']).dt.date

    # Get today's date
    today = datetime.now().date()

    # Filter seminars into upcoming and completed
    upcoming_seminars = seminars_df[seminars_df['Event_Date'] >= today].copy()
    completed_seminars = seminars_df[seminars_df['Event_Date'] < today].copy()

    # --- Create Tabs ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 Upcoming Seminars",
        "✅ My Enrolled Seminars",
        "📝 Seminars to Enroll",
        "📚 Completed Seminars (Peer Learning)"
    ])

    with tab1:
        st.subheader("All Scheduled Future Events")
        display_seminar_list(upcoming_seminars, "Go to Session")

    with tab2:
        st.subheader("Events You Are Registered For")
        enrolled_df = upcoming_seminars[upcoming_seminars['Seminar_Event_Name'].isin(dummy_enrolled_seminars)]
        display_seminar_list(enrolled_df, "Go to Live Session")

    with tab3:
        st.subheader("Available Events You Can Still Join")
        yet_to_enroll_df = upcoming_seminars[~upcoming_seminars['Seminar_Event_Name'].isin(dummy_enrolled_seminars)]
        display_seminar_list(yet_to_enroll_df, "Enroll & Go to Session")

    with tab4:
        st.subheader("Past Seminars for Review and Learning")
        display_seminar_list(completed_seminars, "Review Session")


def display_seminar_list(seminars_df, button_text):
    """Helper function to display a list of seminars in expanders."""
    if seminars_df.empty:
        st.info("No seminars to display in this category.")
        return

    for index, seminar in seminars_df.iterrows():
        with st.expander(f"{seminar['Seminar_Event_Name']} - {seminar['Event_Date'].strftime('%B %d, %Y')}"):
            st.markdown(f"**Domain:** {seminar['Domain']}")
            st.markdown(f"**Description:** {seminar['BriefDescription']}")
            
            if st.button(button_text, key=f"{button_text}_{index}"):
                # Set the selected seminar in the session state and trigger a rerun
                st.session_state.selected_seminar_title = seminar['Seminar_Event_Name']
                # This would ideally navigate to the "Live Session" page.
                # In Streamlit, this is handled by the main app's menu logic,
                # but we can provide feedback here.
                st.success(f"Navigating to '{seminar['Seminar_Event_Name']}'. Please select 'Live Session' from the sidebar.")

