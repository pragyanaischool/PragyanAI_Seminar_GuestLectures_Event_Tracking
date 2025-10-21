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
    stats_tab, user_approval_tab, all_users_tab, seminar_list_tab = st.tabs([
        "📊 Statistics", "⏳ User Approvals", "👥 All Users", "🗓️ Seminar Management"
    ])

    # --- Statistics Tab ---
    with stats_tab:
        st.subheader("Platform Statistics")
        if not users_df.empty and not seminars_df.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Registered Users", len(users_df))
            col2.metric("Total Seminars Planned", len(seminars_df))

            try:
                # Convert 'Event Date' to datetime, coercing errors to NaT (Not a Time)
                seminars_df['Event Date DT'] = pd.to_datetime(seminars_df['Event Date'], errors='coerce')
                
                # Filter out rows where date conversion failed
                valid_seminars = seminars_df.dropna(subset=['Event Date DT'])
                
                upcoming_seminars = valid_seminars[valid_seminars['Event Date DT'] >= datetime.now()]
                col3.metric("Upcoming Seminars", len(upcoming_seminars))
            except KeyError:
                st.warning("'Event Date' column not found in the Seminar Events sheet. Cannot calculate upcoming seminars.")
            except Exception as e:
                st.error(f"An error occurred while calculating statistics: {e}")

        else:
            st.warning("Could not load user or seminar data to display statistics.")
    
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

    # --- All Users Tab ---
    with all_users_tab:
        st.subheader("Full User List")
        if not users_df.empty:
            st.dataframe(users_df, use_container_width=True)
        else:
            st.warning("Could not load user data.")
            
    # --- All Seminars Tab ---
    with seminar_list_tab:
        st.subheader("Full Seminar List & Link Editor")
        st.info("You can edit the seminar links directly in the table below. The Google Sheet will be updated after you finish editing.")
        if seminar_sheet and not seminars_df.empty:
            # Drop the helper datetime column if it exists before displaying
            seminars_to_edit = seminars_df.drop(columns=['Event Date DT'], errors='ignore')
            
            with st.form("seminar_edit_form"):
                edited_seminars_df = st.data_editor(
                    seminars_to_edit,
                    num_rows="dynamic",
                    use_container_width=True,
                    key="seminar_editor"
                )
                
                if st.form_submit_button("Save Changes to Google Sheet"):
                    try:
                        # Overwrite the entire sheet with the updated dataframe
                        db_connector.update_worksheet_with_dataframe(seminar_sheet, edited_seminars_df)
                        st.success("Seminar list updated successfully in Google Sheets!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save changes to Google Sheets: {e}")
        else:
            st.warning("Could not load seminar data.")
            

