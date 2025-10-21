import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Function to connect to Google Sheets
@st.cache_resource
def connect_to_sheet():
    try:
        # Load credentials from Streamlit secrets
        creds_dict = st.secrets["gcp_service_account"]
        scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        return None

# Function to open the user database sheet
def get_user_db(client):
    try:
        # Using the URL provided
        sheet_url = "https://docs.google.com/spreadsheets/d/1nJq-DCS-bGMqtaVvU9VImWhOEet5uuL-uQHcMKBgSss"
        spreadsheet = client.open_by_url(sheet_url)
        worksheet = spreadsheet.worksheet("Users") # Assuming sheet name is "Users"
        return worksheet
    except Exception as e:
        st.error(f"Failed to open user database: {e}")
        return None
        
# Function to open the seminar database sheet
def get_seminar_db(client):
    try:
        sheet_url = "https://docs.google.com/spreadsheets/d/1EeuqOzuc90owGbTZTp7XNJObYkFc9gzbG_v-Mko78mc"
        spreadsheet = client.open_by_url(sheet_url)
        worksheet = spreadsheet.worksheet("Seminars") # Assuming sheet name is "Seminars"
        return worksheet
    except gspread.exceptions.WorksheetNotFound:
        st.error("Worksheet 'Seminars' not found in the Seminar Google Sheet. Please create it.")
        return None
    except Exception as e:
        st.error(f"Failed to open seminar database: {e}")
        return None

# Function to get all users as a DataFrame
def get_users_df(worksheet):
    if worksheet:
        return pd.DataFrame(worksheet.get_all_records())
    return pd.DataFrame()

# Function to get all seminars as a DataFrame
def get_seminars_df(worksheet):
    if worksheet:
        return pd.DataFrame(worksheet.get_all_records())
    return pd.DataFrame()


# Function to add a new user
def add_user(worksheet, user_data):
    try:
        # Appending user data as a new row
        worksheet.append_row(list(user_data.values()))
        return True
    except Exception as e:
        st.error(f"Failed to add user: {e}")
        return False

# Function to update user status or role
def update_user_data(worksheet, phone_number, column_name, new_value):
    """
    Updates a specific cell for a user identified by their login phone number.
    """
    try:
        # Find the column index for the phone number
        headers = worksheet.row_values(1)
        if 'Phone(login)' not in headers:
            st.error("Critical Error: 'Phone(login)' column not found in Users sheet.")
            return False
        
        phone_login_col_index = headers.index('Phone(login)') + 1
        phone_list = worksheet.col_values(phone_login_col_index)
        
        # Find the user's row
        if str(phone_number) in phone_list:
            row_index = phone_list.index(str(phone_number)) + 1
            
            # Find the column index for the data to be updated
            if column_name not in headers:
                st.error(f"Column '{column_name}' not found.")
                return False
            col_index = headers.index(column_name) + 1
            
            # Update the specific cell
            worksheet.update_cell(row_index, col_index, new_value)
            return True
        else:
            st.warning(f"User with phone number {phone_number} not found.")
            return False

    except Exception as e:
        st.error(f"An error occurred while updating the sheet: {e}")
        return False

