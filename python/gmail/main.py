import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        print("Error: token.json file not found. Perform manual authentication first.")
        return None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Error: Credentials are invalid and cannot be refreshed.")
            return None
    service = build('gmail', 'v1', credentials=creds)
    return service

def main():
    service = authenticate_gmail()
    if service:
        # You can test sending an email or any other operation here
        print("Authenticated successfully")


if __name__ == '__main__':
    main()
