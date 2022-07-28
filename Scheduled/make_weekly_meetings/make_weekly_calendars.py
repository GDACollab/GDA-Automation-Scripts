from calendar import calendar
from ics import Calendar, Event
import os
from datetime import timedelta
import re

calendars = {}

def init_calendar_manager():
    global calendars
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
                    print(f"Calendar {entry} added.")
        print(f"Full Calendars: {calendars}")

def calendar_has_event(calendar_name, event_name, date, time=None):
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
def add_event_to_calendar(calendar_name, event_name, date, **kwargs):
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

    if not calendar_name in calendars:
        calendars[calendar_name] = Calendar()
    calendars[calendar_name].events.add(event)

def write_calendars():
    for calendar_name in calendars:
        with open("../calendars/" + calendar_name + ".ics", 'w') as f:
            f.writelines(calendars[calendar_name].serialize_iter())

if __name__ == "__main__":
    # and it's done !
    init_calendar_manager()
    add_event_to_calendar("Test", "This is a test event", "2022-07-27", time="18:00", description="AHA?")
    print(calendar_has_event("Test", "This is a test event", "2022-07-27", "18:00"))
    write_calendars()