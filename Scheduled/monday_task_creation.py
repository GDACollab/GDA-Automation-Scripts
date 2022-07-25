import requests
import json

apiUrl = "https://api.monday.com/v2"
meetings_list = None
meetings_info = None

def setup_monday():
    f = open("monday.json")
    apiKey = json.load(f)["monday.com"]
    f.close()

    global headers
    headers = {"Authorization": apiKey}

def send_request(query_text):
    print(query_text)
    query = query_text
    data = {'query' : query}
    r = requests.post(url = apiUrl, json=data, headers=headers)
    print(r)
    print(r.text)
    print(r.reason)
    return r.text


def load_board_info(board_id):
    board_text = send_request(f"query {{ boards (ids: {board_id}) {{ columns {{ id title }} groups {{ id title }} }}}}")
    board_info = json.loads(board_text)["data"]["boards"][0]
    total_groups = {}
    groups = board_info["groups"]
    for group in groups:
        total_groups[group["title"]] = group["id"]

    total_columns = {}
    columns = board_info["columns"]
    for column in columns:
        total_columns[column["title"]] = column["id"]
    
    return {"groups": total_groups, "columns": total_columns}

# Just to avoid overwhelming requests, we only get the recent tasks:
def has_recent_meeting_task(monday_settings, group, name):
    # And we save the meetings_list as a global for multiple calls (since it's requests to the same board).
    global meetings_list
    if meetings_list == None:
        meetings_name = monday_settings["meetingsBoardId"]
        query = f"query {{ boards (ids: {meetings_name}) {{ items(newest_first: true, limit: 50) {{ name group {{ title }} }} }}}}"
        request = json.loads(send_request(query))
        meetings_list = request["data"]["boards"][0] 

    items = meetings_list["items"]
    for item in items:
        if item["group"]["title"] == group and item["name"] == name:
            return True
    return False

def create_meeting_task(monday_settings, group_name, name, team, date, attatched_file_urls):
    meetings_name = monday_settings["meetingsBoardId"]

    # To avoid repetitive requests, we load meetings info if we don't have it yet:
    global meetings_info
    if meetings_info == None:
        meetings_info = load_board_info(meetings_name)

        
    group_id = meetings_info["groups"][group_name]

    date_name = meetings_info["columns"][monday_settings["date"]]
    docs_name = meetings_info["columns"][monday_settings["docs"]]
    person_name = meetings_info["columns"][monday_settings["person"]]

    files = []
    for file in attatched_file_urls:
        files.append({"name": "Meeting Notes " + date, "fileType": "LINK", "linkToFile": file})

    column_values = {}
    column_values[date_name] = {
        "date": date
    }
    column_values[docs_name] = {
        "files": files
    }
    column_values[person_name] = {
        "personsAndTeams": [{
            "id": team,
            "kind": "team"
        }]
    }

    column_values = json.dumps(column_values)
    column_values = "\"" + column_values.replace("\"", "\\\"") + "\""

    query = f"mutation {{ create_item(board_id: {meetings_name}, group_id: \"{ group_id }\", item_name: \"{name}\", column_values: {column_values}) {{ id }}}}"
    send_request(query)

# For testing:
if __name__ == "__main__":
    setup_monday()

    f = open("settings.json")
    monday_settings = json.load(f)["monday.com"]
    f.close()

    if not has_recent_meeting_task(monday_settings, "Officer Meetings", "Officer Meeting 07/24/2022"):
        create_meeting_task(monday_settings, "Officer Meetings", "New Task Test", 655466, "2022-07-20", ["https://docs.google.com/document/d/1PetNAMsppulIHRMpO7YhA9D6pGZlZCyw_2AeECV-QwQ/edit"])