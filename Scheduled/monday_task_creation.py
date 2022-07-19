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


def load_groups(board_id):
    board_text = send_request(f"query {{ boards (ids: {board_id}) {{ groups {{ id title }} }}}}")
    groups = json.loads(board_text)["data"]["boards"][0]["groups"]
    boards = {}
    for board in groups:
        boards[board["title"]] = board["id"]
    return boards


def create_task(monday_settings, group, name, date, attatched_file_urls):
    meetings_name = monday_settings["meetingsBoard"]
    date_name = monday_settings["date"]
    docs_name = monday_settings["docs"]
    column_values = f"{{\"{date_name}\": {date}, \"{docs_name}\": {attatched_file_urls}}}"
    query = f"mutation {{ create_item(board_id: {meetings_name}, group_id: \"{ group }\", item_name: \"{name}\") {{ id }}}}"
    send_request(query)

# For testing:
if __name__ == "__main__":
    setup_monday()

    f = open("settings.json")
    monday_settings = json.load(f)["monday.com"]
    f.close()

    groups = load_groups(monday_settings["meetingsBoard"])
    create_task(monday_settings, groups["General Meetings"], "New Task Test", "07/20/2022", "[\"https://docs.google.com/document/d/1PetNAMsppulIHRMpO7YhA9D6pGZlZCyw_2AeECV-QwQ/edit\"]")