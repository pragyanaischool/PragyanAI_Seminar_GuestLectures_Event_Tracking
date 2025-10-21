import streamlit as st
import pandas as pd

def admin_main(db_connector):
    """The main function for the Admin Dashboard page."""
    st.title("👑 Admin Dashboard")
    st.info("Manage users and seminar events from this dashboard.")

    # --- Constants for Google Sheets ---
    USER_DATA_URL = "https://docs.google.com/spreadsheets/d/1nJq-DCS-bGMqtaVvU9VImWhOEet5uuL-uQHcMKBgSss/edit?usp=sharing"
    USER_WORKSHEET_NAME = "Users"
    SEMINAR_DATA_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
    SEMINAR_WORKSHEET_NAME = "SeminarEvents"

    # --- Fetch Data ---
    user_sheet = db_connector.get_worksheet(USER_DATA_URL, USER_WORKSHEET_NAME)
    seminar_sheet = db_connector.get_worksheet(SEMINAR_DATA_URL, SEMINAR_WORKSHEET_NAME)

    if not user_sheet or not seminar_sheet:
        st.error("Failed to connect to one or more databases. Please check the sheet URLs and names.")
        return

    users_df = db_connector.get_dataframe(user_sheet)
    seminars_df = db_connector.get_dataframe(seminar_sheet)

    # --- Main Admin Tabs ---
    user_tab, seminar_tab = st.tabs(["User Management", "Seminar Management"])

    with user_tab:
        st.header("User Administration")
        if users_df.empty:
            st.warning("The user database is currently empty.")
        else:
            handle_user_management(db_connector, user_sheet, users_df)

    with seminar_tab:
        st.header("Seminar Event Administration")
        if seminars_df.empty:
            st.warning("No seminars have been created yet.")
        else:
            handle_seminar_management(db_connector, seminar_sheet, seminars_df)


def handle_user_management(db_connector, user_sheet, users_df):
    """Displays UI for managing users."""
    approval_tab, all_users_tab = st.tabs(["Approval Management", "All Users"])

    with approval_tab:
        st.subheader("User Approval Requests")
        approval_df = users_df[users_df['Status'] == 'Not Approved']

        if approval_df.empty:
            st.success("No pending user approvals.")
        else:
            for index, row in approval_df.iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    col1.subheader(row['FullName'])
                    col1.write(f"**Phone:** {row['Phone(login)']}")
                    col1.write(f"**Email:** {row['Email']}")

                    if col2.button("Approve User", key=f"approve_{row['Phone(login)']}", use_container_width=True):
                        if db_connector.update_record(user_sheet, 'Phone(login)', row['Phone(login)'], {'Status': 'Approved'}):
                            st.success(f"Approved {row['FullName']}.")
                            st.rerun()

    with all_users_tab:
        st.subheader("All Registered Users")
        st.dataframe(users_df)

        st.subheader("Promote User Role")
        user_list = users_df['Phone(login)'].tolist()
        selected_user_phone = st.selectbox("Select a user by phone number", user_list)
        
        if selected_user_phone:
            user_data = users_df[users_df['Phone(login)'].astype(str) == str(selected_user_phone)].iloc[0]
            st.write(f"**Current Role for {user_data['FullName']}:** {user_data['Role']}")
            
            new_role = st.selectbox("Select new role", ["Student", "Organizer", "Lead"], index=["Student", "Organizer", "Lead"].index(user_data['Role']))

            if st.button(f"Update Role for {user_data['FullName']}", use_container_width=True):
                if db_connector.update_record(user_sheet, 'Phone(login)', selected_user_phone, {'Role': new_role}):
                    st.success(f"Updated role for {user_data['FullName']} to {new_role}.")
                    st.rerun()

def handle_seminar_management(db_connector, seminar_sheet, seminars_df):
    """Displays UI for managing seminars."""
    st.subheader("Approve Pending Seminars")
    pending_seminars = seminars_df[seminars_df['Status'] == 'Pending']

    if pending_seminars.empty:
        st.success("No seminars are currently pending approval.")
    else:
        for index, row in pending_seminars.iterrows():
            with st.container(border=True):
                st.subheader(row['Seminar Title'])
                st.write(f"**Presenter:** {row['Presenter Name(s)']}")
                st.write(f"**Date:** {row['Date']}")
                
                if st.button("Approve Seminar", key=f"approve_seminar_{row['Seminar Title']}", use_container_width=True):
                    if db_connector.update_record(seminar_sheet, 'Seminar Title', row['Seminar Title'], {'Status': 'Approved'}):
                        st.success(f"Approved seminar: '{row['Seminar Title']}'.")
                        st.rerun()

    st.divider()
    st.subheader("All Seminar Events")
    st.dataframe(seminars_df)


