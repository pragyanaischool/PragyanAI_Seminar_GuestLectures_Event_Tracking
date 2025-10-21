import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from gspread.exceptions import WorksheetNotFound

# Use Streamlit's caching to initialize the connection once.
@st.cache_resource
def get_gspread_client():
    """Establishes a connection to the Google Sheets API and returns the client."""
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        return None

class GoogleSheetsConnector:
    """A class to handle all interactions with the Google Sheets database."""

    def __init__(self):
        """Initializes the connector by getting the gspread client."""
        self.client = get_gspread_client()

    def get_worksheet(self, sheet_url: str, worksheet_name: str):
        """
        Opens a spreadsheet by its URL and returns a specific worksheet.
        
        Args:
            sheet_url (str): The full URL of the Google Sheet.
            worksheet_name (str): The name of the tab/worksheet to open.

        Returns:
            gspread.Worksheet or None: The worksheet object if found, otherwise None.
        """
        if not self.client:
            st.error("Cannot get worksheet: Google Sheets client is not available.")
            return None
        try:
            spreadsheet = self.client.open_by_url(sheet_url)
            return spreadsheet.worksheet(worksheet_name)
        except WorksheetNotFound:
            st.error(f"Worksheet '{worksheet_name}' not found in the Google Sheet. Please check the sheet URL and worksheet name.")
            return None
        except Exception as e:
            st.error(f"Failed to open worksheet '{worksheet_name}': {e}")
            return None

    def get_dataframe(self, worksheet: gspread.Worksheet) -> pd.DataFrame:
        """
        Fetches all records from a worksheet and returns them as a pandas DataFrame.
        """
        if worksheet:
            return pd.DataFrame(worksheet.get_all_records())
        return pd.DataFrame()

    def append_record(self, worksheet: gspread.Worksheet, data_list: list) -> bool:
        """
        Appends a new row of data to the specified worksheet.
        """
        if not worksheet:
            st.error("Cannot append record: Worksheet is not valid.")
            return False
        try:
            worksheet.append_row(data_list)
            return True
        except Exception as e:
            st.error(f"Failed to append record: {e}")
            return False

    def update_record(self, worksheet: gspread.Worksheet, key_column: str, key_value: str, target_column: str, new_value: str) -> bool:
        """
        Updates a specific cell in a worksheet. It finds a row by a key value
        in a key column and updates a cell in the target column of that row.
        """
        if not worksheet:
            st.error("Cannot update record: Worksheet is not valid.")
            return False
        try:
            # Find the row and column indices
            headers = worksheet.row_values(1)
            if key_column not in headers:
                st.error(f"Key column '{key_column}' not found.")
                return False
            if target_column not in headers:
                st.error(f"Target column '{target_column}' not found.")
                return False

            key_col_index = headers.index(key_column) + 1
            target_col_index = headers.index(target_column) + 1

            # Find the cell to update
            cell_list = worksheet.findall(str(key_value), in_column=key_col_index)
            if not cell_list:
                st.warning(f"Record with {key_column} = '{key_value}' not found.")
                return False

            # Update the first matching record's target column
            row_index = cell_list[0].row
            worksheet.update_cell(row_index, target_col_index, new_value)
            return True
        except Exception as e:
            st.error(f"An error occurred while updating the sheet: {e}")
            return False
