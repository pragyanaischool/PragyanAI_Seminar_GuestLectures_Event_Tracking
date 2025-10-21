import streamlit as st
import pandas as pd
from google_sheets_db import (
    connect_to_sheet, 
    get_user_db, 
    get_users_df, 
    update_user_data,
    get_seminar_db,
    get_seminars_df
)

def admin_main():
    # Add logo at the top. Ensure the image file is in the same directory as app.py
    try:
        st.image("PragyanAI_Transperent.png", width=200)
    except FileNotFoundError:
        st.warning("Logo image not found. Please add 'PragyanAI_Transperent.png' to your project directory.")

    st.title("Admin Dashboard")

    client = connect_to_sheet()
    if not client:
        st.stop()
    
    # --- User Management Section ---
    st.header("User Management")
    user_sheet = get_user_db(client)
    if not user_sheet:
        st.error("Could not access the user database.")
    else:
        users_df = get_users_df(user_sheet)
        if users_df.empty:
            st.info("No users have signed up yet.")
        else:
            # --- User Approval List ---
            st.subheader("Pending User Approvals")
            not_approved_users = users_df[users_df['Status'] == 'NotApproved']
            
            if not not_approved_users.empty:
                for index, user in not_approved_users.iterrows():
                    with st.expander(f"{user['FullName']} - {user['Phone(login)']}"):
                        st.write(f"**College:** {user['CollegeName']}")
                        st.write(f"**Branch:** {user['Branch']}")
                        st.write(f"**LinkedIn:** {user['LinkedinProfile']}")
                        st.write(f"**Area of Interest:** {user['Area_of_Interest']}")
                        
                        if st.button(f"Approve {user['FullName']}", key=f"approve_{user['Phone(login)']}"):
                            phone_login = str(user['Phone(login)'])
                            if update_user_data(user_sheet, phone_login, "Status", "Approved"):
                                st.success(f"User {user['FullName']} has been approved.")
                                st.experimental_rerun()
                            else:
                                st.error(f"Failed to approve {user['FullName']}.")
            else:
                st.info("No users are currently pending approval.")

            # --- View All Users & Promote to Organizer ---
            st.subheader("All Registered Users")
            st.dataframe(users_df)

            st.subheader("Promote User to Organizer")
            promotable_users = users_df[~users_df['Role'].isin(['Admin', 'Organizer', 'Lead'])]
            if not promotable_users.empty:
                user_list = promotable_users['FullName'].tolist()
                selected_user_name = st.selectbox("Select a user to promote", user_list)
                
                if st.button("Promote to Organizer"):
                    user_to_promote = users_df[users_df['FullName'] == selected_user_name].iloc[0]
                    phone_number = str(user_to_promote['Phone(login)'])
                    
                    if update_user_data(user_sheet, phone_number, "Role", "Organizer"):
                        st.success(f"{selected_user_name} has been promoted to Organizer.")
                        st.experimental_rerun()
                    else:
                        st.error(f"Failed to promote {selected_user_name}.")
            else:
                st.info("No users available to be promoted.")

    # --- Seminar Management Section ---
    st.header("Seminar Management")
    seminar_sheet = get_seminar_db(client)
    if not seminar_sheet:
        st.error("Could not access the seminar database.")
    else:
        seminars_df = get_seminars_df(seminar_sheet)
        
        st.subheader("View All Seminars")
        if seminars_df.empty:
            st.info("No seminars have been created yet.")
        else:
            st.dataframe(seminars_df)

        st.subheader("Approve Seminar Events")
        if 'Status' in seminars_df.columns:
            pending_seminars = seminars_df[seminars_df['Status'] == 'Pending']
            if not pending_seminars.empty:
                 for index, seminar in pending_seminars.iterrows():
                    # Assuming a unique identifier like 'Seminar ID' exists
                    seminar_id = seminar.get('Seminar ID', f"seminar_{index}")
                    with st.expander(f"{seminar.get('Seminar Title', 'No Title')} by {seminar.get('Organizer Name', 'N/A')}"):
                        st.write(f"**Date:** {seminar.get('Date', 'N/A')}")
                        st.write(f"**Description:** {seminar.get('Description', 'N/A')}")
                        
                        if st.button(f"Approve '{seminar.get('Seminar Title', 'No Title')}'", key=f"approve_seminar_{seminar_id}"):
                            # Note: This requires an 'update_seminar_data' function
                            st.info("Seminar approval functionality is under development.")
            else:
                st.info("No seminars are currently pending approval.")
        else:
            st.warning("To enable approvals, please add a 'Status' column to your Seminars Google Sheet.")

