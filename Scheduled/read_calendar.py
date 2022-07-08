import json
import re

def range_to_tuple(range_str):
    return (ord(range_str[0].upper()) - ord('A'), int(range_str[1]))

def get_curr_range(spreadsheet):
    values = spreadsheet.get('values', [])
    curr_range = None
    for i in range(0, len(values)):
        row = values[i]
        for j in range(0, len(row)):
            col = row[j]
            if col == "AUTOMATION_TODAY=":
                curr_range = [row[j + 1], row[j + 2]]
                break
        if curr_range != None:
            break
    # Since we already have the full range, let's just convert it into actual indices:
    if curr_range != None:
        for i in range(len(curr_range)):
            # In case the selected range has a $ sign for reference:
            ref_removed = curr_range[i].replace("$", "")
            curr_range[i] = range_to_tuple(ref_removed)
    return curr_range

def get_func_called(string):
    match = re.search(string, "\(\"[A-Za-z ]+\"\)")
    if match:
        return (match.string[:match.span()[0]], get_func_args(match.group()))
    else:
        return None

def get_func_args(called):
    # Remove ("")
    args = called.sub[3:-2]
    return args.split(",")

def copying_set(enabled, args, settings):
    settings["docsToCopy"][args[0]] = enabled

def write_settings(sheet_service, settings):
    # The spreadsheet will dictate to us what range to search for keywords.
    spreadsheet = sheet_service.values().get(settings["masterCalendar"]).execute()
    curr_range = get_curr_range(spreadsheet)
    if curr_range == None:
        print("Could not find current date range for read_calendar.py. Check https://docs.google.com/document/d/14Tb3xYnoqSR5jlgUHWEKbHgXnAZKVc1V9sFDW5kJ4b4/edit?usp=sharing for details.")
        return
    
    # Now we search through the range we're given:
    for i in range(curr_range[0][0], curr_range[1][0]):
        row = spreadsheet[i]
        for j in range(curr_range[0][1], curr_range[1][1]):
            col = spreadsheet[j]

            func = get_func_called(col)
            if func:
                args = func[1]
                funcs = {
                    "COPY_START": copying_set(True, args, settings),
                    "COPY_END": copying_set(False, args, settings)
                }
                if func[0] in funcs:
                    funcs[func[0]]()
                else:
                    print(f"Could not find function {func[0]} to execute")

    s = open("settings.json", 'w')
    json.dump(settings, s)
    s.close()