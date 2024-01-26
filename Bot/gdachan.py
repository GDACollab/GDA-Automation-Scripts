import json, discord, os, sys
from datetime import datetime, timedelta
from drive_login import login

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# From https://stackoverflow.com/questions/4060221/how-to-reliably-open-a-file-in-the-same-directory-as-the-currently-running-scrip
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def read_attendance_csv(path):
	if not os.path.exists(path):
		return None, None

	# Just read the metadata, don't try to do anything fancy:
	metadata = os.stat(path)
	last_date = metadata.st_mtime

	id_file = path.replace(".csv", ".id")

	existing_id = None
	if os.path.exists(id_file):
		with open(id_file, 'r') as file:
			existing_id = file.read()
	return existing_id, datetime.fromtimestamp(last_date)

def upload_file_to_drive(path, name, existing_id=None):
	if not os.path.exists(path):
		print(f"Error, cannot upload {name} to drive with existing id {existing_id}. {path} does not exist.")
		return
	global drive

	if existing_id != None:
		try:
			drive.files().get(fileId=existing_id, fields='id', supportsAllDrives=True).execute()
		except HttpError as e:
			print(f"{existing_id} does not likely exist on the drive. Error: {e}")
			existing_id = None

	csv = MediaFileUpload(path, mimetype='text/csv')
	metadata = {'name': name, 'mimeType': 'text/csv'}
	print(f"Loading {path}")

	id_file = open(path.replace(".csv", ".id"), "a")
	try:
		if existing_id == None:
			metadata["parents"] = ["1DjNOtRnlhhiEMFk-Y3UO4WuWIndZuixB"]
			file = drive.files().create(body=metadata, media_body=csv, fields='id', supportsAllDrives=True).execute()
			existing_id = file.get('id')
			print(f"Uploaded {name} with file ID: {existing_id}")
		else:
			file = drive.files().update(fileId=existing_id, body=metadata, media_body=csv, fields='id', supportsAllDrives=True).execute()
			existing_id = file.get('id')
			print(f"Updated {name} with file ID: {existing_id}")
		id_file.write(f"{existing_id}")
	except HttpError as error:
		print(f"Error uploading {name}: {error}")
	
	id_file.close()

async def read_vc_users(file_path, date_string, time_string):
	
	new_file = not os.path.exists(file_path)
	f = open(file_path, "a")

	print("Server Name,Channel ID,Channel Name,Date,Time,# of Members")
	if new_file:
		f.write("Server Name,Channel ID,Channel Name,Date,Time,# of Members\n")

	header = f"---,---,---,{date_string},{time_string},---\n"
	print(header)
	f.write(header)

	async for guild in client.fetch_guilds():
		if not guild.unavailable:
			channels = await guild.fetch_channels()
			for c in channels:
				if type(c) == discord.VoiceChannel:
					# We have to fetch directly from the client for some reason to see members.
					try:
						channel = await client.fetch_channel(c.id)
						if len(channel.members) > 0:
							entry = f"{guild.name},{channel.id},{channel.name},{date_string},{time_string},{len(channel.members)}\n"
							f.write(entry)
							print(entry)
					except discord.Forbidden:
						# I don't know how else to check to see if there isn't a permission error. I literally have to fetch the channel to see if there's an error in viewing it.
						pass
		else:
			# Unavailable
			entry = f"{guild.name},OFFLINE,ALL OFFLINE,{date_string},{time_string},OFFLINE\n"
			f.write(entry)
			print(entry)
	f.close()


@client.event
async def on_ready():
	print(f"Logged in as {client.user}\n")
	try:
		await client.change_presence(status=discord.CustomActivity("owo"))

		d = datetime.now()
		date_string = d.strftime("%Y/%m/%d")
		time_string = d.strftime("%H:%M:%S")
		month_string = d.strftime("%Y_%B")

		file_name = f"{month_string}_voice_attendance.csv"
		file_path= os.path.join(__location__, file_name)
		
		existing_id, date_modified = read_attendance_csv(file_path)

		await read_vc_users(file_path, date_string, time_string)

		
		# Is this the first time we're writing to today?
		# This ensures we upload the file to drive at most once per day.
		print("Existing ID: ", existing_id, "Date Modified: ", date_modified)
		if existing_id is None or (date_modified is not None and date_modified.date() != d.date()):
			# Are we even in the same month as the last recorded date?
			# Existing_id is only None when either: the file hasn't been uploaded to the drive yet (which should happen every time it's created).
			# OR when we're in a new month.
			if existing_id == None:
				previous_month_full = (d - timedelta(weeks=1)).strftime("%Y_%B")
				previous_file_name = f"{previous_month_full}_voice_attendance.csv"
				previous_file_path = os.path.join(__location__, file_name.replace(".csv", ".id"))
				print(f"Uploading previous month {previous_month_full}, with path {previous_file_path}.")
				if previous_file_name != file_name and os.path.exists(previous_file_path):
					upload_file_to_drive(previous_file_path, previous_file_name)

			# Regardless, upload today's drive file:
			upload_file_to_drive(file_path, file_name, existing_id)
	except Exception as error:
		import traceback
		traceback.print_exc()
	await client.close()

if __name__ == "__main__":
	args = sys.argv[1:]
	if len(args) > 0 and (args[0] == "--login" or args[0] == "-l"):
		print(login())
		exit(0)
	else:
		try:
			global drive
			creds = login()
			drive = build('drive', 'v3', credentials=creds)

			token = os.path.join(__location__, "token.json")
			with open(token) as f:
				data = json.load(f)
				client.run(data["token"])
		except HttpError as error:
			print(f'An error has occured: {error}')
			exit(error)