import os.path

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# This was initially done by logging in through the GDA google account. But the refresh token is alarmingly short, so I'm tinkering with service accounts to get this working. Check the documentation here: https://docs.google.com/document/d/15y5yf16ZrhVHdGhMKeectQK4fSh4FQJbK2RczCBoOh8/edit?usp=sharing
# For how to get it working for you.

# I thought limiting the amount of files this thing has access to might be useful in case something goes terribly wrong and starts deleting everything.
# So we can make files SPECIFIC to this app. We only want to upload files to the drive, so this allows that.
# It also prevents the deletion or viewing of files this app hasn't created (at least supposedly, anyways):
SCOPES = ['https://www.googleapis.com/auth/drive.file']

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

def login():
    
    creds = Credentials.from_service_account_file(os.path.join(__location__, 'gcredentials.json'), scopes=SCOPES)
    return creds