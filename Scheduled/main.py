import sys
import os.path
import json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from drive_login import login, full_login_refresh
from make_weekly_docs import make_docs
from read_calendar import read_calendar

def main():
    args = sys.argv[1:]

    # If we just want to do an initial login process:
    if len(args) > 0 and (args[0] == "--login" or args[0] == "-l"):
        if os.path.exists('token.json'):
            os.remove('token.json')
        full_login_refresh()
        exit(0)

    try:
        s = open('settings.json')
        settings = json.load(s)
        s.close()
        creds = login()

        # Should have permission to do this with current scopes. Add https://www.googleapis.com/auth/spreadsheets.readonly otherwise
        sheet_service = build('sheets', 'v4', credentials=creds)
        read_calendar(sheet_service, settings)

        creds = login()
        service = build('drive', 'v3', credentials=creds)
        make_docs(service, settings)

    except HttpError as error:
        print(f'An error has occured: {error}')

if __name__ == "__main__":
    main()