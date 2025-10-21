import streamlit as st
import pandas as pd

# --- Constants ---
USER_DATA_URL = "https://docs.google.com/spreadsheets/d/1nJq-DCS-bGMqtaVvU9VImWhOEet5uuL-uQHcMKBgSss/edit?usp=sharing"
USER_WORKSHEET_NAME = "Users"
SEMINAR_DATA_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
SEMINAR_WORKSHEET_NAME = "SeminarEvents"

def admin_main(db_connector):
    """
    The main function for the Admin Dashboard page.
    This function now accepts a db_connector object.
    """
    st.header("👑 Admin Dashboard")

    try:
        st.image("PragyanAI_Transperent.png", width=200)
    except Exception as e:
        pass # Logo is optional here

    # --- Tabbed Interface for Admin Functions ---
    user_management_tab, seminar_management_tab = st.tabs(["User Management", "Seminar Management"])

    with user_management_tab:
        manage_user_approvals(db_connector)
        promote_users_to_organizer(db_connector)

    with seminar_management_tab:
        view_all_seminars(db_connector)
        # Placeholder for approving seminar events
        st.subheader("Approve Seminar Events")
        st.info("Feature to approve seminars coming soon.")

def manage_user_approvals(db_connector):
    """Displays users awaiting approval and allows admin to approve them."""
    st.subheader("User Approval List")
    user_sheet = db_connector.get_worksheet(USER_DATA_URL, USER_WORKSHEET_NAME)
    if not user_sheet:
        return

    users_df = db_connector.get_dataframe(user_sheet)
    if users_df.empty:
        st.info("No users found in the database.")
        return

    # Ensure 'Status' column exists before filtering
    if 'Status' in users_df.columns:
        not_approved_users = users_df[users_df['Status'] == 'Not Approved']
        if not not_approved_users.empty:
            st.write("The following users are awaiting approval:")
            for index, user in not_approved_users.iterrows():
                col1, col2 = st.columns([3, 1])
                col1.write(f"**Name:** {user['FullName']} | **Phone:** {user['Phone(login)']}")
                if col2.button("Approve", key=f"approve_{user['Phone(login)']}"):
                    success = db_connector.update_record(
                        user_sheet,
                        key_column='Phone(login)',
                        key_value=user['Phone(login)'],
                        target_column='Status',
                        new_value='Approved'
                    )
                    if success:
                        st.success(f"Approved {user['FullName']}.")
                        st.rerun()
                    else:
                        st.error(f"Failed to approve {user['FullName']}.")
        else:
            st.success("No users are currently awaiting approval.")
    else:
        st.error("The 'Users' sheet is missing the 'Status' column.")

def promote_users_to_organizer(db_connector):
    """Allows admin to select a user and promote them to the 'Organizer' role."""
    st.subheader("Promote User to Organizer")
    user_sheet = db_connector.get_worksheet(USER_DATA_URL, USER_WORKSHEET_NAME)
    if not user_sheet:
        return

    users_df = db_connector.get_dataframe(user_sheet)
    if users_df.empty:
        return

    # Ensure 'Role' and 'Status' columns exist
    if 'Role' in users_df.columns and 'Status' in users_df.columns:
        approved_students = users_df[(users_df['Role'] == 'Student') & (users_df['Status'] == 'Approved')]
        if not approved_students.empty:
            user_options = {f"{row['FullName']} ({row['Phone(login)']})": row['Phone(login)'] for index, row in approved_students.iterrows()}
            selected_user_display = st.selectbox("Select a user to promote:", list(user_options.keys()))

            if st.button("Promote to Organizer"):
                user_phone = user_options[selected_user_display]
                success = db_connector.update_record(
                    user_sheet,
                    key_column='Phone(login)',
                    key_value=user_phone,
                    target_column='Role',
                    new_value='Organizer'
                )
                if success:
                    st.success(f"Successfully promoted {selected_user_display.split(' (')[0]} to Organizer.")
                    st.rerun()
                else:
                    st.error("Failed to promote user.")
        else:
            st.info("No approved students available to promote.")
    else:
        st.error("The 'Users' sheet is missing 'Role' or 'Status' columns.")


def view_all_seminars(db_connector):
    """Displays a list of all seminars from the seminar events sheet."""
    st.subheader("All Seminar Events")
    seminar_sheet = db_connector.get_worksheet(SEMINAR_DATA_URL, SEMINAR_WORKSHEET_NAME)
    if not seminar_sheet:
        return

    seminars_df = db_connector.get_dataframe(seminar_sheet)
    if not seminars_df.empty:
        st.dataframe(seminars_df)
    else:
        st.info("No seminar events have been created yet.")
        
