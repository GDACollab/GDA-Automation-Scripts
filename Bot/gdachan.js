const {Client, Events, GatewayIntentBits, ChannelType} = require("discord.js");

const { token, drive_token } = require('./token.json');

const fs = require("fs");

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

async function readVCUsers(c) {
	let d = new Date();
	let date = d.toLocaleDateString("en-us");
	let time = d.toLocaleTimeString("en-us");
	var guilds = Array.from((await c.guilds.fetch()).values());
	if (!fs.existsSync("./vc.csv")) {
		fs.writeFileSync("./vc.csv", "Server Name,Channel Name,Date,Time,# of Members\n");
	}
	let writer = fs.createWriteStream("./vc.csv", {
		flags: "a"
	});
	for (var g of guilds) {
		var guild = await g.fetch();
		if (guild.available) {
			var channels = Array.from((await guild.channels.fetch()).values());
			for (var channel of channels) {
				if (channel.type === ChannelType.GuildVoice) {
					writer.write(`${guild.name},${channel.name},${date},${time},${channel.members.size}\n`);
				}
			}
		}
	}
	writer.end();
	// process.exit(0);
}

async function writeToDrive() {
	
}

client.once(Events.ClientReady, c=> {
	console.log(`Logged in as ${c.user.tag}`);

	readVCUsers(c);
});

client.login(token);