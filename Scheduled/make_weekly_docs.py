import json
import datetime

from monday_task_creation import create_meeting_task, load_board_info

# I'm currently documenting how I intend for this all to work in https://docs.google.com/document/d/14Tb3xYnoqSR5jlgUHWEKbHgXnAZKVc1V9sFDW5kJ4b4/edit?usp=sharing
# So go check that out.


# For settings.json, under docsToCopy...
# I don't know how the drive will be structured in the future, so this solution may require some editing if it ever gets restructured.
# For right now though, I'm just going to use the file IDs for everything in order to get this working
# You can change which files are accessed by going into drive, going to the link in drive where it says something like:
# https://docs.google.com/document/d/ID/edit
# or https://drive.google.com/drive/u/0/folders/ID
# And just copy and pasting the ID part. Should work for slides or docs. You might have to expand scopes for other files if you want those duplicated.

# Get the current monday of this week. Add or subtract days as needed.
def get_week_monday(offset="Monday"):
    offsets = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5, #Stupid week conventions:
        "Sunday": -1,
        "NextWeek": 7
    }

    today = datetime.date.today()
    return today + datetime.timedelta(days=-(today.weekday())) + datetime.timedelta(days=offsets[offset])

def make_docs(service, settings):

    # ID of the officer drive. Not sure we need it right now?
    officer_drive = settings["officerDrive"]
    monday_board_info = load_board_info(settings["monday.com"]["meetingsBoardId"])

    for doc in settings["docsToCopy"]:
        date = get_week_monday("Sunday")
        if settings["docsToCopy"][doc]["makeNextWeek"]:
            date = get_week_monday("NextWeek")

        date_string = f"{date.year}/{date.month}/{date.day}"

        name = f"[{date_string}] Week Of {doc}"
        # Specifics on using q= to search for files: https://developers.google.com/drive/api/guides/search-files#python
        current_files = service.files().list(q=f"name='{name}'", includeItemsFromAllDrives=True, supportsTeamDrives=True).execute()
        # If we're currently allowed to make the document, and if the document we're trying to make doesn't exist:
        if settings["docsToCopy"][doc]["enabled"] and len(current_files.get("files")) <= 0:
            body = {
                "name": name,
                "parents": [
                    settings["docsToCopy"][doc]["folder"]
                ]
            }
            file = service.files().copy(fileId=settings["docsToCopy"][doc]["file"], supportsAllDrives=True, body=body).execute()
            create_meeting_task(settings["monday.com"], monday_board_info, settings["docsToCopy"][doc]["name"], name, settings["docsToCopy"][doc]["teamId"], date_string, [file["webViewLink"]])