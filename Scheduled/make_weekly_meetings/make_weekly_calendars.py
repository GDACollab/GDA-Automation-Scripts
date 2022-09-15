from calendar import calendar
from ics import Calendar, Event, Attendee
import pytz
import os
from datetime import datetime
import re

calendars = {}
gcalendars = {}

def init_calendar_manager(calendar_service=None):
    global calendars
    global gcalendars
    if not os.path.exists("../calendars"):
        os.mkdir("../calendars")
    else:
        with os.scandir("../calendars/") as dirs:
            for e in dirs:
                entry = e.name
                if re.search(".ics$", entry):
                    f = open("../calendars/" + entry, "r")
                    calendars[entry.replace(".ics", "")] = Calendar(f.read())
                    f.close()
                    print(f"ICS Calendar {entry} added.")

    if calendar_service != None:
        gcal_items = calendar_service.calendarList().list().execute()["items"]
        for calendar in gcal_items:
            print(f"Gcal {calendar} located. Adding local events...")
            gcalendars[calendar["summary"]] = {"id": calendar["id"], "events": calendar_service.events().list(calendar["id"])["items"]}

def calendar_has_event_ics(calendar_name, event_name, date, time=None):
    if calendar_name in calendars:
        calendar = calendars[calendar_name]
        for event in calendar.events:
            if event.name == event_name:
                if time != None:
                    time_str = event.begin.strftime("%Y-%m-%d %H:%M")
                    return time_str == date + " " + time
                else:
                    time_str = event.begin.strftime("%Y-%m-%d")
                    return time_str == date
        return False
    else:
        print(f"Error: Calendar {calendar_name} not found.")
        return False

# Creates an event and adds it to a calendar. Makes a new calendar if the calendar has not been found.
# Required Arguments:
# calendar_name - Name of the calendar for the event to be added to.
# event_name - Name of the event to make.
# date - The date when the event takes place. Should be formatted "YYYY-MM-DD".
# Optional Arguments:
# time - The time when the event takes place. Should be formatted "HH:MM" (military time).
# url - Attached url.
# description - Attached description.
# Attendees - A list of emails to add as people attending.
def add_event_to_calendar_ics(calendar_name, event_name, date, **kwargs):
    event = Event()
    event.name = event_name
    date_str = date
    if "time" in kwargs:
        time = kwargs["time"]
        date_str += f" {time}"
    event.begin = date_str
    #event.duration = datetime.timedelta(hours=1)

    if "url" in kwargs:
        event.url = kwargs["url"]
    
    if "description" in kwargs:
        event.description = kwargs["description"]

    if "attendees" in kwargs:
        attendees_list = []
        for email in kwargs["attendees"]:
            attendees_list.append(Attendee(email))
        event.attendees = attendees_list

    if not calendar_name in calendars:
        calendars[calendar_name] = Calendar()
    calendars[calendar_name].events.add(event)

# Same as calendar_has_event_ics but for gcal instead.
def calendar_has_event_gcal(calendar_name, event_name, date, time=None):
    if calendar_name in gcalendars:
        calendar = gcalendars[calendar_name]
        for event in calendar["events"]:
            if event["summary"] == event_name:
                if time != None and "dateTime" in event:
                    time_str = event["dateTime"]
                    date_format = date + " " + time
                    date_format = datetime.strptime(date, "")
                    return time_str == date_format.isoformat()
                elif "date" in event:
                    time_str = event["date"]
                    return time_str == date
        return False
    else:
        print(f"Error: Calendar {calendar_name} not found.")
        return False
# Same as above, but works for gcal instead.
def add_event_to_calendar_gcal(calendar_service, calendar_name, event_name, date, **kwargs):
    event = {
        'summary': event_name,
        'start': {
            'timeZone': 'America/Los_Angeles'
        }
    }

    if "time" in kwargs:
        time = kwargs["time"]
        date += f" {time}"
        date_format = datetime.strptime(date, "%Y-%m-%d %H:%M")
        # Has to be formatted to RFC3339, like https://stackoverflow.com/questions/8556398/generate-rfc-3339-timestamp-in-python
        # Switch to UTC timezone:
        date_format.replace(tzinfo=pytz.UTC)
        event["start"]["date"] = date_format.isoformat()
    else:
        event["start"]["date"] = date
    
    if "url" in kwargs:
        event["fileUrl"] = kwargs["url"]
    
    if "description" in kwargs:
        event["description"] = kwargs["description"]
    
    if "attendees" in kwargs:
        attendees_list = []
        for email in kwargs["attendees"]:
            attendees_list.append({"email": email})
        event["attendees"] = attendees_list
    
    if not calendar_name in gcalendars:
        gcalendars[calendar_name] = calendar_service.calendars().insert(body={"summary": calendar_name}).execute()
    
    e = calendar_service.events().insert(calendarId=gcalendars[calendar_name]["id"], body=event).execute()
    gcalendars[calendar_name]["events"].append(e)
        
        

    

def write_calendars():
    for calendar_name in calendars:
        with open("../calendars/" + calendar_name + ".ics", 'w') as f:
            f.writelines(calendars[calendar_name].serialize_iter())

if __name__ == "__main__":
    from drive_login import login
    from googleapiclient.discovery import build

    creds = login()
    calendar_service = build('calendars', 'v3', credentials=creds)

    # and it's done !
    init_calendar_manager(calendar_service)
    #add_event_to_calendar_ics("Test", "This is a test event", "2022-07-27", time="18:00", description="AHA?")
    #print(calendar_has_event_ics("Test", "This is a test event", "2022-07-27", "18:00"))

    add_event_to_calendar_gcal("[Officer] Game Design & Art Collaboration", "This is a test event", "2022-07-27", time="18:00", description="AHA?")
    print(calendar_has_event_gcal("[Officer] Game Design & Art Collaboration", "This is a test event", "2022-07-27", "18:00"))
    #write_calendars()