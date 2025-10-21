import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

class GoogleSheetsConnector:
    """A class to interact with Google Sheets."""

    def __init__(self):
        self.creds = self._get_credentials()
        self.client = self._get_client()

    @st.cache_resource
    def _get_credentials(_self):
        """Get credentials from Streamlit secrets."""
        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            return Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=scopes,
            )
        except Exception as e:
            st.error(f"Failed to load credentials: {e}")
            return None

    @st.cache_resource
    def _get_client(_self):
        """Get the gspread client, authorized with credentials."""
        if _self.creds:
            return gspread.authorize(_self.creds)
        return None

    def get_worksheet(self, sheet_url, worksheet_name):
        """Gets a specific worksheet (tab) from a Google Sheet."""
        if not self.client:
            st.error("Gspread client not initialized. Check credentials.")
            return None
        try:
            spreadsheet = self.client.open_by_url(sheet_url)
            return spreadsheet.worksheet(worksheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            st.error(f"Spreadsheet not found at URL: {sheet_url}")
        except gspread.exceptions.WorksheetNotFound:
            st.error(f"Worksheet '{worksheet_name}' not found in the spreadsheet.")
        except Exception as e:
            st.error(f"An error occurred while accessing the sheet: {e}")
        return None

    def get_dataframe(self, worksheet):
        """Converts a worksheet into a pandas DataFrame."""
        if worksheet:
            return pd.DataFrame(worksheet.get_all_records())
        return pd.DataFrame()

    def add_record(self, worksheet, row_data):
        """Appends a new row of data to the worksheet."""
        try:
            worksheet.append_row(row_data)
            return True
        except Exception as e:
            st.error(f"Failed to add record: {e}")
            return False

    def update_record(self, worksheet, lookup_col, lookup_val, update_data):
        """Updates a specific record in the worksheet."""
        try:
            cell = worksheet.find(str(lookup_val), in_column=worksheet.headers.index(lookup_col) + 1)
            row_index = cell.row
            for col_name, new_val in update_data.items():
                col_index = worksheet.headers.index(col_name) + 1
                worksheet.update_cell(row_index, col_index, new_val)
            return True
        except (gspread.exceptions.CellNotFound, ValueError, AttributeError):
            st.error(f"Could not find record where {lookup_col} is {lookup_val}.")
        except Exception as e:
            st.error(f"Failed to update record: {e}")
        return False

