import discord
from discord import app_commands
import os
from dotenv import load_dotenv
import json
import datetime
load_dotenv()
token = os.getenv("token")
MY_GUILD = discord.Object(id=1222003824689025127)

PingRolesPath = "PingRoles.json"
with open(PingRolesPath , "r") as f:
    PingRoles = json.load(f)
UserPings = {}

class MyClient(discord.Client):

    def __init__(self, intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)



intents = discord.Intents.default() # fix perms
intents.messages = True
intents.message_content = True
intents.members = True
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command(name="ping", description="Ping the Role associated with this Channel")
@app_commands.describe(message='What you want to say in the ping!')
async def ping(interaction: discord.Interaction, message: str):
    minutes = 5
    if interaction.channel_id in PingRoles:
        if str(interaction.user.id) in UserPings:
            minutes_ago = ((datetime.datetime.now() - UserPings[str(interaction.user.id)]).total_seconds() / 60)
            if minutes > minutes_ago:
                timeStr = divmod((minutes - minutes_ago)*60, 60)
                await interaction.response.send_message("You have to wait {} minutes and {} seconds to do that!".format(int(timeStr[0]), int(timeStr[1])  ), ephemeral=True) # make private message
            else:
                await interaction.response.send_message("<@&{}> {}".format(PingRoles[str(interaction.channel_id)], message), allowed_mentions=discord.AllowedMentions(roles=True))
                UserPings[str(interaction.user.id)] = datetime.datetime.now()
        else:
            await interaction.response.send_message("<@&{}> {}".format(PingRoles[str(interaction.channel_id)], message), allowed_mentions=discord.AllowedMentions(roles=True))
            UserPings[str(interaction.user.id)] = datetime.datetime.now()
    else:
        await interaction.response.send_message("You can't do that in this channel")


@client.tree.command(name="set_role", description="Set Ping Role for this Channel")
@app_commands.default_permissions()
@app_commands.describe(role='Role')
async def set_role(interaction: discord.Interaction, role: discord.Role):
    PingRoles[str(interaction.channel_id)] = str(role.id)
    with open(PingRolesPath , "w") as f:
        json.dump(PingRoles, f)
    await interaction.response.send_message("Done!")



client.run(token)