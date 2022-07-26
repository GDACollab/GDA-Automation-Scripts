from icalendar import Calendar, Event, vCalAddress, vText
import os

calendars = {}

def init_calendar_manager():
    global calendars
    if os.path.exists("../calendars"):
        with os.scandir("../calendars/") as dirs:
            for entry in dirs:
                print(entry)

def calendar_has_event(calendar_name, event_name, date, time=None):
    if os.path.exists("../calendars"):
        f = open("../calendars/" + calendar_name, "wb")
