import json
import re

def range_to_tuple(range_str):
    # Subtract one from the row because we're using array notation
    return (ord(range_str[0].upper()) - ord('A'), int(range_str[1]) - 1)

def get_curr_range(values):
    curr_range = None
    for i in range(0, len(values)):
        row = values[i]
        for j in range(0, len(row)):
            col = row[j]
            if col == "AUTOMATION_TODAY=":
                curr_range = [row[j + 1], row[j + 2]]
                print(f"Raw Range: {curr_range}")
                break
        if curr_range != None:
            break
    # Since we already have the full range, let's just convert it into actual indices:
    if curr_range != None:
        for i in range(len(curr_range)):
            # In case the selected range has a $ sign for reference:
            ref_removed = curr_range[i].replace("$", "")
            curr_range[i] = range_to_tuple(ref_removed)
    print(f"Range: {curr_range}")
    return curr_range

def get_func_args(called):
    # Remove ("")
    args = called.sub[3:-2]
    return args.split(",")

def get_func_called(string):
    match = re.search(string, "\(\"[A-Za-z ]+\"\)")
    print(f"Func Match: {match}")
    if match:
        return (match.string[:match.span()[0]], get_func_args(match.group()))
    else:
        return None

def copying_set(enabled, args, settings):
    settings["docsToCopy"][args[0]] = enabled

def read_calendar(sheet_service, settings):
    # The spreadsheet will dictate to us what range to search for keywords.
    # Selecting Sheet1 to pull from is mostly arbitrary. At least this way if someone makes a new sheet, they won't have to do more fiddling to get this part right.
    spreadsheet = sheet_service.spreadsheets().values().get(spreadsheetId=settings["masterCalendar"], range="Sheet1").execute()
    values = spreadsheet['values']
    curr_range = get_curr_range(values)
    if curr_range == None:
        print("Could not find current date range for read_calendar.py. Check https://docs.google.com/document/d/14Tb3xYnoqSR5jlgUHWEKbHgXnAZKVc1V9sFDW5kJ4b4/edit?usp=sharing for details.")
        return
    
    # Now we search through the range we're given. We add 1 because we want it to be inclusive.
    for i in range(curr_range[0][1], curr_range[1][1] + 1):
        # Because the cells exclude blank rows and columns, so we don't count them in our search:
        if i <= len(values) - 1:
            row = values[i]
            for j in range(curr_range[0][0], curr_range[1][0] + 1):
                if j <= len(row) - 1:
                    col = row[j]

                    func = get_func_called(col)
                    print(f"Func called: {func}")
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