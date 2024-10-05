import gspread
import logging
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

class DataManager:
    def __init__(self, json_keyfile_path: str, spreadsheet_id: str):
        # Path to the Google Sheets API JSON credentials and sheet name
        self.json_keyfile_path = json_keyfile_path
        self.spreadsheet_id = spreadsheet_id

        # Setup Google Sheets API credentials
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.json_keyfile_path, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(self.spreadsheet_id).sheet1

        # Initialize Google Drive API client
        self.drive_service = build('drive', 'v3', credentials=creds)

    def update_data(self, row_data):
        """Append a new row to the Google Sheet."""
        try:
            self.sheet.append_rows(row_data)
            logging.info(f"Row added to Google Sheets: {row_data}")
        except Exception as e:
            logging.error(f"Error adding row to Google Sheets: {e}")
