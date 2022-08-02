import json
import datetime

from make_weekly_meetings.monday_task_creation import create_meeting_task, has_recent_meeting_task, setup_monday
from make_weekly_meetings.make_weekly_docs import get_if_meeting_doc_exists, copy_doc, extract_file_id
from make_weekly_meetings.make_weekly_calendars import calendar_has_event, add_event_to_calendar, init_calendar_manager

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
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5, #Stupid week conventions:
        "sunday": -1, # In case we don't want to wait next week to make docs:
        "nextweeksunday": 6
    }

    today = datetime.date.today()
    return today + datetime.timedelta(days=-(today.weekday())) + datetime.timedelta(days=offsets[offset.lower()])

def init_meeting_creation():
    init_calendar_manager()
    setup_monday()

def make_meetings(service, settings):
    for doc in settings["docsToCopy"]:
        docSettings = settings["docsToCopy"][doc]

        date = get_week_monday("Sunday")
        if "date" in docSettings:
            date = get_week_monday(docSettings["date"]["day"])

        month = str(date.month)
        day = str(date.day)
        if len(month) == 1:
            month = "0" + month
        if len(day) == 1:
            day = "0" + day
        date_string = f"{date.year}/{month}/{day}"

        name = f"[{date_string}] {doc}"
        # If we're currently allowed to make the document, and if the document we're trying to make doesn't exist:
        if "enabled" in docSettings and docSettings["enabled"]:
            link = None
            # If we have files and folders to copy from Google Drive:
            if "file" in docSettings and "folder" in docSettings:
                link = get_if_meeting_doc_exists(service, name)
                if link == False:
                    link = copy_doc(service, extract_file_id(docSettings["file"]), extract_file_id(docSettings["folder"]), name)

            # Same thing, but for Monday.com tasks:
            if "monday.com" in docSettings and not has_recent_meeting_task(settings["monday.com"], docSettings["monday.com"]["name"], name):
                kwargs = {}
                if "date" in docSettings:
                    kwargs["date"] = {
                        "date": date_string.replace("/", "-")
                    }
                    if "time" in docSettings["date"]:
                        kwargs["date"]["time"] = docSettings["date"]["time"]
                
                if "teamId" in docSettings["monday.com"]:
                    kwargs["team_id"] = docSettings["monday.com"]["teamId"]
                
                if link != None:
                    kwargs["attached_file_urls"] = [link]
                
                create_meeting_task(settings["monday.com"], docSettings["monday.com"]["name"], name, **kwargs)
            
            if "date" in docSettings:
                kwargs = {}
                if "time" in docSettings["date"]:
                    kwargs["time"] = docSettings["date"]["time"]

                if link != None:
                    kwargs["url"] = link
                add_event_to_calendar(doc, name, date_string.replace("/", "-"), time=docSettings["date"]["time"])
