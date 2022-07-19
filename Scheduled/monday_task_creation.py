import requests
import json

apiUrl = "https://api.monday.com/v2"

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


def create_meeting_task(monday_settings, board_info, group, name, team, date, attatched_file_urls):
    meetings_name = monday_settings["meetingsBoardId"]
    date_name = board_info["columns"][monday_settings["date"]]
    docs_name = board_info["columns"][monday_settings["docs"]]
    person_name = board_info["columns"][monday_settings["person"]]

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
        "id": team,
        "kind": "team"
    }

    column_values = json.dumps(column_values)
    column_values = "\"" + column_values.replace("\"", "\\\"") + "\""
    query = f"mutation {{ create_item(board_id: {meetings_name}, group_id: \"{ group }\", item_name: \"{name}\", column_values: {column_values}) {{ id }}}}"
    send_request(query)

# For testing:
if __name__ == "__main__":
    setup_monday()

    f = open("settings.json")
    monday_settings = json.load(f)["monday.com"]
    f.close()

    info = load_board_info(monday_settings["meetingsBoardId"])
    create_meeting_task(monday_settings, info, "General Meetings", "New Task Test", "655466", "2022-07-20", ["https://docs.google.com/document/d/1PetNAMsppulIHRMpO7YhA9D6pGZlZCyw_2AeECV-QwQ/edit"])