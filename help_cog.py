import discord
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = ""
        self.text_channel_list = []
        self.set_message()

    def set_message(self):
        self.help_message = f"""
```
General commands:
{self.bot.command_prefix} help - Displays all the available commands
{self.bot.command_prefix} q - Displays the current quran queue
{self.bot.command_prefix} p <keywords> - Finds the surat on youtube and plays it in your current channel. Will resume playing the current surat if it was paused
{self.bot.command_prefix} skip - Skips the current surat being played
{self.bot.command_prefix} clear - Stops all the surats and clears the queue
{self.bot.command_prefix} stop - Disconnected the bot from the voice channel
{self.bot.command_prefix} pause - Pauses the current surat being played or resumes if already paused
{self.bot.command_prefix} resume - Resumes playing the current surat
{self.bot.command_prefix} prefix - Change command prefix
{self.bot.command_prefix} remove - Removes last surat from the queue
```
"""

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(f"type {self.bot.command_prefix}help"))

    @commands.command(name="help", help="Displays all the available commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)
    
    @commands.command(name="prefix", help="Change bot prefix")
    async def prefix(self, ctx, *args):
        self.bot.command_prefix = " ".join(args)
        self.set_message()
        await ctx.send(f"prefix set to **'{self.bot.command_prefix}'**")
        await self.bot.change_presence(activity=discord.Game(f"type {self.bot.command_prefix}help"))

    @commands.command(name="send_to_all", help="send a message to all members")
    async def send_to_all(self, msg):
        for text_channel in self.text_channel_list:
            await text_channel.send(msg)
