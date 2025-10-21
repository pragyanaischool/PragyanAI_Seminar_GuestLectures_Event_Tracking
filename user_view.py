import streamlit as st
import pandas as pd

# --- Constants ---
SEMINAR_DATA_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
SEMINAR_WORKSHEET_NAME = "SeminarEvents"

def user_main(db_connector):
    """
    The main function for the User Home page.
    This function now accepts a db_connector object.
    """
    st.header("🏠 Home")
    try:
        st.image("PragyanAI_Transperent.png", width=200)
    except Exception as e:
        pass  # Logo is optional here

    st.write(f"Welcome to the PragyanAI Seminar Platform, {st.session_state.user_name}!")
    st.info("Here you can view upcoming seminars and access live sessions.")

    st.subheader("Upcoming Seminars")

    # Fetch and display seminar events
    seminar_sheet = db_connector.get_worksheet(SEMINAR_DATA_URL, SEMINAR_WORKSHEET_NAME)
    if seminar_sheet:
        seminars_df = db_connector.get_dataframe(seminar_sheet)
        if not seminars_df.empty:
            # Display seminars in a more user-friendly format
            for index, row in seminars_df.iterrows():
                with st.container():
                    st.markdown(f"#### {row.get('Seminar Title', 'No Title')}")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Date", str(row.get('Date', 'TBA')))
                    col2.metric("Time", str(row.get('Time', 'TBA')))
                    col3.metric("Presenter", str(row.get('Presenter Name(s)', 'N/A')))
                    st.markdown(f"**Description:** {row.get('Seminar Description', 'No description available.')}")
                    st.link_button("Go to Live Session", url="#") # Placeholder link
                    st.divider()
        else:
            st.info("There are no upcoming seminars scheduled at the moment.")
    else:
        st.error("Could not retrieve the list of seminars.")
        
