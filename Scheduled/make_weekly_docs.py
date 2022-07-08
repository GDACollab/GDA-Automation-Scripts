import os.path
import sys
import json
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# I'm currently documenting how I intend for this all to work in https://docs.google.com/document/d/14Tb3xYnoqSR5jlgUHWEKbHgXnAZKVc1V9sFDW5kJ4b4/edit?usp=sharing
# So go check that out.


# For settings.json, under docsToCopy...
# I don't know how the drive will be structured in the future, so this solution may require some editing if it ever gets restructured.
# For right now though, I'm just going to use the file IDs for everything in order to get this working
# You can change which files are accessed by going into drive, going to the link in drive where it says something like:
# https://docs.google.com/document/d/ID/edit
# or https://drive.google.com/drive/u/0/folders/ID
# And just copy and pasting the ID part. Should work for slides or docs. You might have to expand scopes for other files if you want those duplicated.

# I thought limiting the amount of files this thing has access to might be useful in case something goes terribly wrong and starts deleting everything.
# So we can only look at and make files SPECIFIC to this app. That basically means we're allowed to look at files and copy them to other places. No deleting.
# If you feel this somehow needs to be expanded, you can add the https://www.googleapis.com/auth/drive.readonly. You also have to make sure the OAuth consent screen has the
# relevant scopes enabled.
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.readonly']

def login():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES
    )
    creds = flow.run_local_server(port=0)
    return creds

def save(creds):
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

# Get the current monday of this week. Add or subtract days as needed.
def get_week_monday(offset="Monday"):
    offsets = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }

    today = datetime.date.today()
    return today + datetime.timedelta(days=-(today.weekday())) + datetime.timedelta(days=offsets[offset])

def make_docs(service):
    s = open('settings.json')
    settings = json.load(s)
    s.close()

    # ID of the officer drive. Not sure we need it right now?
    officer_drive = settings["officerDrive"]

    for doc in settings["docsToCopy"]:
        date = get_week_monday(doc["dayOfWeek"])
        date_string = f"{date.year}/{date.month}/{date.day}"

        name = f"[{date_string}] {doc['name']}"
        # Specifics on using q= to search for files: https://developers.google.com/drive/api/guides/search-files#python
        current_files = service.files().list(q=f"name='{name}'", includeItemsFromAllDrives=True, supportsTeamDrives=True).execute()
        # If we're currently allowed to make the document, and if the document we're trying to make doesn't exist:
        if doc["enabled"] and len(current_files.get("files")) <= 0:
            body = {
                "name": name,
                "parents": [
                    doc["folder"]
                ]
            }
            service.files().copy(fileId=doc["file"], supportsAllDrives=True, body=body).execute()

# Borrowing some code from google's python quickstart: https://developers.google.com/drive/api/quickstart/python in case anyone wants to check that out.
def main():
    args = sys.argv[1:]

    # If we just want to do an initial login process:
    if len(args) > 0 and (args[0] == "--login" or args[0] == "-l"):
        if os.path.exists('token.json'):
            os.remove('token.json')
        save(login())
        exit(0)
    
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
            creds = login()
        save(creds)
    
    try:
        service = build('drive', 'v3', credentials=creds)
        make_docs(service)
    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()
