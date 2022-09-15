import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# I thought limiting the amount of files this thing has access to might be useful in case something goes terribly wrong and starts deleting everything.
# So we can only look at and make files SPECIFIC to this app. That basically means we're allowed to look at files and copy them to other places. No deleting.
# If you feel this somehow needs to be expanded, you can add the https://www.googleapis.com/auth/drive.readonly. You also have to make sure the OAuth consent screen has the
# relevant scopes enabled.

# Also added control over calendars for subscribable gcal events with attendees.
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/calendar']

def login_refresh():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES
    )
    creds = flow.run_local_server(port=0)
    return creds

def save(creds):
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

def full_login_refresh():
    save(login_refresh())

def login():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = login_refresh()
        save(creds)
    return creds