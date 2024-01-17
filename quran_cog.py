from ast import alias
import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
import asyncio

class quran_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        #all the quran related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [surat, channel]
        self.quran_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best'}
        self.FFMPEG_OPTIONS = {'options': '-vn'}

        self.vc = None
        self.ytdl = YoutubeDL(self.YDL_OPTIONS)

     #searching the item on youtube
    def search_yt(self, item):
        if item.startswith("https://"):
            title = self.ytdl.extract_info(item, download=False)["title"]
            return{'source':item, 'title':title}
        search = VideosSearch(item, limit=1)
        return{'source':search.result()["result"][0]["link"], 'title':search.result()["result"][0]["title"]}

    async def play_next(self):
        if len(self.quran_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.quran_queue[0][0]['source']

            #remove the first element as you are currently playing it
            self.quran_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            surat = data['url']
            self.vc.play(discord.FFmpegPCMAudio(surat, executable= "ffmpeg.exe", **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
        else:
            self.is_playing = False

    # infinite loop checking 
    async def play_quran(self, ctx):
        if len(self.quran_queue) > 0:
            self.is_playing = True

            m_url = self.quran_queue[0][0]['source']
            #try to connect to voice channel if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.quran_queue[0][1].connect()

                #in case we fail to connect
                if self.vc == None:
                    await ctx.send("```Could not connect to the voice channel```")
                    return
            else:
                await self.vc.move_to(self.quran_queue[0][1])
            #remove the first element as you are currently playing it
            self.quran_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            surat = data['url']
            self.vc.play(discord.FFmpegPCMAudio(surat, executable= "ffmpeg.exe", **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))

        else:
            self.is_playing = False

    @commands.command(name="play", aliases=["p","playing"], help="Plays a selected surat from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except:
            await ctx.send("```You need to connect to a voice channel first!```")
            return
        if self.is_paused:
            self.vc.resume()
        else:
            surat = self.search_yt(query)
            if type(surat) == type(True):
                await ctx.send("```Could not download the surat. Incorrect format try another keyword. This could be due to playlist or a livestream format.```")
            else:
                if self.is_playing:
                    await ctx.send(f"**#{len(self.quran_queue)+2} -'{surat['title']}'** added to the queue")  
                else:
                    await ctx.send(f"**'{surat['title']}'** added to the queue")  
                self.quran_queue.append([surat, voice_channel])
                if self.is_playing == False:
                    await self.play_quran(ctx)

    @commands.command(name="pause", help="Pauses the current surat being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name = "resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the current surat being played")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_quran(ctx)


    @commands.command(name="queue", aliases=["q"], help="Displays the current surat in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.quran_queue)):
            retval += f"#{i+1} -" + self.quran_queue[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(f"```queue:\n{retval}```")
        else:
            await ctx.send("```No surat in queue```")

    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the surat and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.quran_queue = []
        await ctx.send("```Quran queue cleared```")

    @commands.command(name="stop", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
    
    @commands.command(name="remove", help="Removes last surat added to queue")
    async def re(self, ctx):
        self.quran_queue.pop()
        await ctx.send("```last surat removed```")
