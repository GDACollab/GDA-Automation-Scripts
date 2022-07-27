import json
import re
from make_weekly_meetings.make_weekly_docs import extract_file_id

def range_to_tuple(range_str):
    # Subtract one from the row because we're using array notation
    return (ord(range_str[0].upper()) - ord('A'), int(range_str[1:]) - 1)

def get_curr_range(values):
    ranges_dict = {}
    for i in range(0, len(values)):
        row = values[i]
        for j in range(0, len(row)):
            col = row[j]
            if re.search("AUTOMATION_[\w]+=", col):
                name = col.replace("AUTOMATION_", "")
                name = name.replace("=", "")
                ranges_dict["automation_" + name.lower()] = [row[j + 1], row[j + 2]]

    # Since we already have the full range, let's just convert it into actual indices:
    if ranges_dict != {}:
        for (key, value) in ranges_dict:
            for i in range(len(value)):
                # In case the selected range has a $ sign for reference:
                ref_removed = value[i].replace("$", "")
                value[i] = range_to_tuple(ref_removed)
                ranges_dict[key] = value
    print(f"Range: {ranges_dict}")
    return ranges_dict

def read_automation_json(curr_range, values):
    keys = []
    json_dict = {}
    # Now we search through the range we're given. We add 1 because we want it to be inclusive.
    for i in range(curr_range[0][1], curr_range[1][1] + 1):
        # Because the cells exclude blank rows and columns, so we don't count them in our search:
        if i <= len(values) - 1:
            row = values[i]
            json_object = {}
            for j in range(curr_range[0][0], curr_range[1][0] + 1):
                if j <= len(row) - 1:
                    col = row[j]
                    if len(keys) == 0:
                        keys.append(col)
                    else:
                        # We assume the first value is always the key:
                        if j == 0:
                            json_dict[col] = json_object
                        else:
                            # If the column is blank, we don't want to worry about it:
                            if col == "":
                                continue
                            # Do we have a column formatted like {"json": "data"}? If yes, load that in as new json data.
                            try:
                                loaded_json = json.loads(col)
                                json_object[values[j]] = loaded_json
                            except ValueError as e:
                                if col.lower() == "true" or col.lower() == "false":
                                    if col.lower() == "true":
                                        json_object[values[j]] = True
                                    else:
                                        json_object[values[j]] = False
                                else:
                                    json_object[values[j]] = col
            json_dict[row[curr_range[0][0]]] = json_object
    return json_dict

def read_calendar(sheet_service, settings):
    # The spreadsheet will dictate to us what range to search for keywords.
    # Selecting Sheet1 to pull from is mostly arbitrary. At least this way if someone makes a new sheet, they won't have to do more fiddling to get this part right.
    spreadsheet = sheet_service.spreadsheets().values().get(spreadsheetId=extract_file_id(settings["masterCalendar"]), range="Sheet1").execute()
    values = spreadsheet['values']
    range_dict = get_curr_range(values)
    if range_dict == {}:
        print("Could not find AUTOMATION_ ranges for read_calendar.py. Check https://docs.google.com/document/d/14Tb3xYnoqSR5jlgUHWEKbHgXnAZKVc1V9sFDW5kJ4b4/edit?usp=sharing for details.")
        return
    
    for (key, curr_range) in range_dict:
        if re.search("_json$"):
            doc_json = read_automation_json(curr_range, values)

            # Now to find where we're writing all of this data in settings.json:
            json_pointer = re.sub("^settings->", "", values[curr_range[0][0]])
            location_pointer = json_pointer.split("->")
            curr_location = settings
            for location in location_pointer:
                if location != "":
                    curr_location = curr_location[location]

            for (key, value) in doc_json:
                curr_location[key] = value

    s = open("settings.json", 'w')
    # From https://stackoverflow.com/questions/37398301/json-dumps-format-python
    json.dump(settings, s, sort_keys=True, indent=4, separators=(',', ': '))
    s.close()