import json, discord, datetime, os.path
from datetime import datetime

# From https://stackoverflow.com/questions/4060221/how-to-reliably-open-a-file-in-the-same-directory-as-the-currently-running-scrip
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def read_vc_users():
	d = datetime.now()
	date_string = d.strftime("%Y/%m/%d")
	time_string = d.strftime("%H:%M:%S")
	
	vc = os.path.join(__location__, "./vc.csv")
	new_file = not os.path.exists(vc)
	f = open(vc, "a")

	if new_file:
		f.write("Server Name,Channel Name,Date,Time,# of Members\n")

	async for guild in client.fetch_guilds():
		if not guild.unavailable:
			channels = await guild.fetch_channels()
			for channel in channels:
				if type(channel) == discord.VoiceChannel:
					f.write(f"{guild.name},{channel.name},{date_string},{time_string},{len(channel.members)}\n")
		else:
			# Unavailable
			f.write(f"{guild.name},ALL OFFLINE,{date_string},{time_string},OFFLINE\n")
	f.close()


@client.event
async def on_ready():
	print(f"Logged in as {client.user}")
	await read_vc_users()
	await client.close()


if __name__ == "__main__":
	with open(os.path.join(__location__, 'token.json')) as f:
		data = json.load(f)
		client.run(data["token"])