import streamlit as st
import pandas as pd
from datetime import datetime
import gspread # To find cell and update

def admin_main(db_connector):
    """The main function for the Admin Dashboard page."""
    st.title("👑 Admin Dashboard")
    st.markdown("---")

    # --- Define constants for Google Sheets ---
    USER_SHEET_URL = "https://docs.google.com/spreadsheets/d/1nJq-DCS-bGMqtaVvU9VImWhOEet5uuL-uQHcMKBgSss/edit?usp=sharing"
    SEMINAR_SHEET_URL = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc/edit?usp=sharing"
    
    USER_WORKSHEET_NAME = "Users"
    SEMINAR_WORKSHEET_NAME = "Seminar Events" # Please ensure this is the exact name of the tab in your sheet

    # --- Data Loading and Caching ---
    @st.cache_data(ttl=60) # Cache for 1 minute to keep data fresh
    def load_data():
        try:
            user_sheet = db_connector.get_worksheet(USER_SHEET_URL, USER_WORKSHEET_NAME)
            users_df = db_connector.get_dataframe(user_sheet) if user_sheet else pd.DataFrame()

            seminar_sheet = db_connector.get_worksheet(SEMINAR_SHEET_URL, SEMINAR_WORKSHEET_NAME)
            seminars_df = db_connector.get_dataframe(seminar_sheet) if seminar_sheet else pd.DataFrame()
            
            return users_df, seminars_df, user_sheet, seminar_sheet
        except Exception as e:
            st.error(f"Failed to load data from Google Sheets: {e}")
            return pd.DataFrame(), pd.DataFrame(), None, None

    users_df, seminars_df, user_sheet, seminar_sheet = load_data()

    # --- Tabbed Interface ---
    all_users_tab, user_approval_tab, seminar_list_tab, seminar_approval_tab, seminar_update_tab = st.tabs([
        "👥 All Users", "⏳ Users for Approvals", "🗓️ All Seminar Events", "⏳ Seminars for Approvals", "✍️ Update Seminar Info"
    ])

    # --- All Users Tab ---
    with all_users_tab:
        st.subheader("Full User List")
        if not users_df.empty:
            st.dataframe(users_df, use_container_width=True)
        else:
            st.warning("Could not load user data.")
            
    # --- User Approval Tab ---
    with user_approval_tab:
        st.subheader("Users Waiting for Approval")
        if user_sheet and not users_df.empty:
            pending_users = users_df[users_df['Status'] == 'Not Approved']

            if not pending_users.empty:
                st.info(f"You have **{len(pending_users)}** user(s) to approve.")
                
                for index, user in pending_users.iterrows():
                    with st.container(border=True):
                        st.write(f"**Name:** {user['FullName']}")
                        st.text(f"Phone: {user['Phone(login)']}")
                        st.text(f"Email: {user.get('Email', 'N/A')}")
                        
                        if st.button("Approve User", key=f"approve_{user['Phone(login)']}"):
                            try:
                                cell = user_sheet.find(str(user['Phone(login)']))
                                headers = user_sheet.row_values(1)
                                status_col_index = headers.index('Status') + 1
                                user_sheet.update_cell(cell.row, status_col_index, 'Approved')
                                st.success(f"Approved {user['FullName']}!")
                                st.cache_data.clear()
                                st.rerun()
                            except gspread.exceptions.CellNotFound:
                                st.error(f"Could not find user with phone {user['Phone(login)']} in the sheet to approve.")
                            except ValueError:
                                st.error("Critical error: Could not find the 'Status' column header in the Users sheet.")
                            except Exception as e:
                                st.error(f"An error occurred while approving: {e}")
            else:
                st.success("No users are currently waiting for approval. Great job! ✅")
        else:
            st.warning("Could not load user data to check for approvals.")

    # --- All Seminars Tab ---
    with seminar_list_tab:
        st.subheader("Full Seminar List")
        if not seminars_df.empty:
            st.dataframe(seminars_df, use_container_width=True)
        else:
            st.warning("Could not load seminar data.")

    # --- Seminar Approvals Tab ---
    with seminar_approval_tab:
        st.subheader("Seminars Waiting for Approval")
        st.warning("Feature in development. To enable seminar approvals, please add a 'Status' column to your 'Seminar Events' Google Sheet.", icon="⚠️")
        # Placeholder for future functionality
        # if not seminars_df.empty and 'Status' in seminars_df.columns:
        #     ... # Approval logic here
        # else:
        #     st.info("Seminar approval feature requires a 'Status' column in the sheet.")


    # --- Update Seminar Info Tab ---
    with seminar_update_tab:
        st.subheader("Select a Seminar to Update")
        if seminar_sheet and not seminars_df.empty and 'Seminar Event Topic' in seminars_df.columns:
            
            # Use a unique key for the selectbox to avoid state issues
            seminar_topics = seminars_df['Seminar Event Topic'].tolist()
            selected_topic = st.selectbox(
                "Choose a seminar:",
                options=seminar_topics,
                index=None, # No default selection
                placeholder="Select a seminar event...",
                key="seminar_update_select"
            )

            if selected_topic:
                # Get the full record for the selected seminar
                seminar_data = seminars_df[seminars_df['Seminar Event Topic'] == selected_topic].iloc[0]
                
                st.markdown(f"### Editing: **{selected_topic}**")
                
                with st.form(key="update_seminar_form"):
                    
                    # Create a dictionary to hold the updated data
                    updated_values = {}
                    
                    # Dynamically create text inputs for each column
                    for col_name in seminars_df.columns:
                        updated_values[col_name] = st.text_input(
                            f"{col_name}",
                            value=str(seminar_data.get(col_name, ""))
                        )

                    submit_button = st.form_submit_button("Update Seminar Details")

                    if submit_button:
                        try:
                            # Find the row in the sheet using the unique Seminar Event Topic
                            cell = seminar_sheet.find(selected_topic)
                            
                            if not cell:
                                st.error(f"Could not find the seminar '{selected_topic}' in the sheet to update.")
                                return

                            sheet_row_number = cell.row
                            
                            # Convert dictionary values to a list in the correct order
                            new_row_data = [updated_values[col] for col in seminars_df.columns]
                            
                            # Update the specific row in the Google Sheet
                            seminar_sheet.update(f"A{sheet_row_number}", [new_row_data])
                            
                            st.success(f"Successfully updated '{selected_topic}'!")
                            st.cache_data.clear() # Clear cache to fetch new data
                            st.rerun()

                        except gspread.exceptions.CellNotFound:
                            st.error(f"Could not find the seminar '{selected_topic}' in the sheet to update.")
                        except Exception as e:
                            st.error(f"An error occurred while updating the seminar: {e}")
        else:
            st.warning("Could not load seminar data or 'Seminar Event Topic' column not found.")
