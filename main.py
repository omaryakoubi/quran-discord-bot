import discord
from discord.ext import commands
import os, asyncio

#import all of the cogs
from help_cog import help_cog
from quran_cog import quran_cog

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

#remove the default help command so that we can write out own
bot.remove_command('help')

async def main():
    async with bot:
        await bot.add_cog(help_cog(bot))
        await bot.add_cog(quran_cog(bot))
        await bot.start(os.getenv['TOKEN'])

asyncio.run(main())

