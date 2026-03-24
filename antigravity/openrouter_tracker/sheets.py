import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_service():
    """Shows basic usage of the Sheets API.
    Returns a service object.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.get_refresh_token():
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("\n[ERROR] 'credentials.json' not found!")
                print("Please follow the README.md to download your OAuth 2.0 secrets from Google Cloud Console.")
                print("Save it as 'credentials.json' in this directory and re-run the script.\n")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8555)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)
        return service
    except HttpError as err:
        print(f"An error occurred building service: {err}")
        return None

def create_spreadsheet(service, title="OpenRouter Performance Stats"):
    """Creates a new spreadsheet."""
    try:
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                                    fields='spreadsheetId').execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        print(f"Created Spreadsheet ID: {spreadsheet_id}")
        
        # Initialize headers
        init_headers(service, spreadsheet_id)
        return spreadsheet_id
    except HttpError as err:
        print(f"An error occurred creating spreadsheet: {err}")
        return None

def init_headers(service, spreadsheet_id):
    """Initializes sheet with headers."""
    values = [
        ["Timestamp", "Model ID", "Provider", "Latency (s)", "Throughput (tps)", "Uptime (%)"]
    ]
    append_rows(service, spreadsheet_id, values)

def append_rows(service, spreadsheet_id, values, range_name="Sheet1!A1"):
    """Appends rows to the spreadsheet."""
    try:
        body = {
            'values': values
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption="USER_ENTERED", body=body).execute()
        print(f"{result.get('updates').get('updatedCells')} cells appended.")
    except HttpError as err:
        print(f"An error occurred appending rows: {err}")

if __name__ == "__main__":
    # Test execution
    print("Testing Sheets module...")
    service = get_service()
    if service:
        # Create a test spreadsheet if needed
        # spreadsheet_id = create_spreadsheet(service, "Test OpenRouter")
        # print(f"Test Spreadhseet ID: {spreadsheet_id}")
        pass
