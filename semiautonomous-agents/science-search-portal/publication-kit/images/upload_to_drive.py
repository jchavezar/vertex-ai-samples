#!/usr/bin/env python3
"""Upload architecture diagrams to Google Drive artifacts folder."""

import os
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import google.auth

# Artifacts folder ID in Google Drive
ARTIFACTS_FOLDER_ID = "1K2lkvQYuWd3SN8gg9R7obL9GQ2juFj7e"

def get_credentials():
    """Get credentials using gcloud."""
    # Use ADC (Application Default Credentials)
    creds, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/drive.file'])
    return creds

def upload_file(service, filepath, folder_id):
    """Upload a file to Google Drive."""
    filename = os.path.basename(filepath)

    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }

    media = MediaFileUpload(filepath, mimetype='image/png')

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink'
    ).execute()

    return file

def main():
    # Get credentials
    creds = get_credentials()

    # Build Drive service
    service = build('drive', 'v3', credentials=creds)

    # Find all PNG files in current directory
    png_files = [f for f in os.listdir('.') if f.endswith('.png') and f.startswith(('01', '02', '03', '04', '05'))]

    print(f"Found {len(png_files)} diagram files to upload")

    for filepath in sorted(png_files):
        print(f"Uploading {filepath}...")
        try:
            result = upload_file(service, filepath, ARTIFACTS_FOLDER_ID)
            print(f"  ✓ Uploaded: {result.get('name')}")
            print(f"    Link: {result.get('webViewLink', 'N/A')}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")

if __name__ == '__main__':
    main()
