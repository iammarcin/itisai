import os
import re
import base64
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.base import MIMEBase
from email import encoders

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

def search_emails(service, query='', max_results=10, label_ids=None):
    """
    Search emails with custom queries.

    Parameters:
    - service: Authenticated Gmail API service instance.
    - query: String, search query (e.g., 'from:someone@example.com subject:test').
    - max_results: Integer, maximum number of results to return.
    - label_ids: List of strings, label IDs to filter messages by.

    Returns:
    - List of dictionaries containing email data.
    """
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results, labelIds=label_ids).execute()
        messages = results.get('messages', [])
        emails = []
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            emails.append(msg_data)
        return emails
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def download_attachments(service, message):
    """
    Download attachments from a message.

    Parameters:
    - service: Authenticated Gmail API service instance.
    - message: Message object from which to download attachments.

    Returns:
    - List of file paths to the downloaded attachments.
    """
    attachments = []
    for part in message['payload'].get('parts', []):
        if part['filename']:
            sanitized_filename = sanitize_filename(part['filename'])
            if 'data' in part['body']:
                data = part['body']['data']
            else:
                att_id = part['body'].get('attachmentId')
                att = service.users().messages().attachments().get(userId='me', messageId=message['id'], id=att_id).execute()
                data = att['data']
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
            path = os.path.join('/tmp', sanitized_filename)
            with open(path, 'wb') as f:
                f.write(file_data)
            attachments.append(path)
    return attachments


def send_email(service, sender, to, subject, message_text, cc=None, bcc=None, attachments=None):
    """
    Create and send an email.

    Parameters:
    - service: Authenticated Gmail API service instance.
    - sender: String, email address of the sender.
    - to: String, email address of the receiver.
    - subject: String, subject of the email.
    - message_text: String, body text of the email.
    - cc: String, email address(es) to send a copy.
    - bcc: String, email address(es) to send a blind copy.
    - attachments: List of file paths to attach.

    Returns:
    - Sent message.
    """
    try:
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc
        msg = MIMEText(message_text)
        message.attach(msg)

        if attachments:
            for file in attachments:
                with open(file, 'rb') as f:
                    mime_base = MIMEBase('application', 'octet-stream')
                    mime_base.set_payload(f.read())
                    encoders.encode_base64(mime_base)
                    mime_base.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file)}')
                    message.attach(mime_base)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {'raw': raw}
        sent_message = service.users().messages().send(userId='me', body=body).execute()
        return sent_message
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# to avoid problems with filenames (it happened!)
def sanitize_filename(filename):
    # Replace problematic characters with an underscore
    return re.sub(r'[\/:*?"<>|]', '_', filename)


def main():
    service = authenticate_gmail()
    if service:
        # Get sender and recipient from environment variables
        sender = os.getenv('EMAIL_SENDER')
        recipient = os.getenv('EMAIL_TO')
        if not sender or not recipient:
            print("Error: EMAIL_SENDER or EMAIL_TO environment variable not set.")
            return

        # Search for emails
        emails = search_emails(service, query='subject:Boarding', max_results=10)
        all_attachments = []
        for email in emails:
            print(email['snippet'])
            attachments = download_attachments(service, email)
            all_attachments.extend(attachments)

        # Send email with the collected attachments
        sent_message = send_email(service, sender=sender, to=recipient, subject='Test Subject', message_text='This is a test email with attachments.', attachments=all_attachments)
        if sent_message:
            print("Email sent successfully")
