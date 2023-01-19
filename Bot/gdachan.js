const {Client, Events, GatewayIntentBits, ChannelType} = require("discord.js");

const { token } = require('./token.json');

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

async function readVCUsers(c) {
	var guilds = Array.from((await c.guilds.fetch()).values());
	guilds.forEach(async (guild) => {
		var g = await guild.fetch();
		if (g.available) {
			var channels = Array.from((await g.channels.fetch()).values());
			channels.forEach(channel => {
				if (channel.type === ChannelType.GuildVoice) {
					console.log(channel.members.size);
				}
			});
		}
	});
}

client.once(Events.ClientReady, c=> {
	console.log(`Logged in as ${c.user.tag}`);
	readVCUsers(c);
});

client.login(token);