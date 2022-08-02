import re
# Returns a link if it finds the document. Otherwise, returns false:
def get_if_meeting_doc_exists(drive_service, name):
    # Specifics on using q= to search for files: https://developers.google.com/drive/api/guides/search-files#python
    current_files = drive_service.files().list(q=f"name='{name}'", includeItemsFromAllDrives=True, supportsTeamDrives=True).execute()
    if len(current_files.get("files")) > 0:
        return "https://docs.google.com/document/d/" + current_files["files"][0]["id"] + "/edit"
    else:
        return False

# Copies a doc based on:
# file_id - The ID of the file to copy
# folder_id - The folder to put it in
# name - The name of the new file
# Returns a link to the new file.
def copy_doc(drive_service, file_id, folder_id, name):
    body = {
        "name": name,
        "parents": [
            folder_id
        ]
    }
    file = drive_service.files().copy(fileId=file_id, supportsAllDrives=True, body=body, fields="webViewLink").execute()
    return file["webViewLink"]

# Extracts file id from a link. This should work even if the "link" is just the file id itself:
def extract_file_id(link):
    id_str = re.search("(\/)*[\d\w-]{9,}(\/)*", link)
    id_str = id_str.group().replace("/", "")
    return id_str