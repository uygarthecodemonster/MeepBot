import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_unread_emails():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)

        results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=5).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No unread emails, Boss! Time to fap more!")
            return
        
        print("Here are your last 5 unread emails, Boss:")

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='metadata', metadataHeaders=['Subject', 'From', 'Date']).execute()

            headers = msg['payload']['headers']
            subject = 'No Subject'
            sender = 'Unknown Sender'
            date = msg['internalDate']

            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                if header['name'] == 'From':
                    sender = header['value']
                if header['name'] == 'Date':
                    raw_date = header['value']               
                    dt_object = parsedate_to_datetime(raw_date)
                    local_dt = dt_object.astimezone() 
                    clean_date = local_dt.strftime("%b %d at %H:%M")

            print(f"From: {sender}, Subject: {subject}, Date: {clean_date}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    get_unread_emails()
        