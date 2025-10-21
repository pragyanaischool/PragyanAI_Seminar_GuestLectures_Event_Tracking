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

# Function to get all users as a DataFrame
def get_users_df(worksheet):
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
