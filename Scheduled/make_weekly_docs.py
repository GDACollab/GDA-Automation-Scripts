import json
import datetime

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
        "Sunday": -1
    }

    today = datetime.date.today()
    return today + datetime.timedelta(days=-(today.weekday())) + datetime.timedelta(days=offsets[offset])

def make_docs(service, settings):

    # ID of the officer drive. Not sure we need it right now?
    officer_drive = settings["officerDrive"]

    for doc in settings["docsToCopy"]:
        date = get_week_monday("Sunday")
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