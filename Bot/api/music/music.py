import asyncio
import os
from functools import partial

import discord
from async_timeout import timeout
from discord.ext import commands
from youtube_dl import YoutubeDL

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(title)s-%(id)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class NoMusicFileError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.

        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, player, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()
        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)
        # 用關鍵字搜尋或是撥放清單的情形
        if 'entries' in data:
            # 格式: data['entries']為list 存放歌曲
            await ctx.send('資料較多... 請稍待....')

            if download:
                for entry in data['entries']:
                    await player.queue.put(cls(discord.FFmpegPCMAudio(ytdl.prepare_filename(entry)), data=entry,
                                               requester=ctx.author))
                    await ctx.send(f'```\n[已增加 {entry["title"]} 到撥放序列中]\n```', delete_after=15)
            else:
                for entry in data['entries']:
                    await player.queue.put({'webpage_url': entry['webpage_url'], 'requester': ctx.author,
                                            'title': entry['title']})
                    await ctx.send(f'```\n[已增加 {entry["title"]} 到撥放序列中]\n```', delete_after=15)
        else:
            if download:
                await player.queue.put(cls(discord.FFmpegPCMAudio(ytdl.prepare_filename(data)), data=data, requester=ctx.author))
                await ctx.send(f'```\n[已增加 {data["title"]} 到撥放序列中]\n```', delete_after=15)
            else:
                await player.queue.put({'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']})
                await ctx.send(f'```\n[已增加 {data["title"]} 到撥放序列中]\n```', delete_after=15)

    @classmethod
    async def create_local_source(cls, ctx, filename: str, *, loop):
        loop = loop or asyncio.get_event_loop()

        if os.path.isfile(f'.\\music\\{filename}'):
            source = discord.FFmpegPCMAudio(f'.\\music\\{filename}')
        else:
            raise NoMusicFileError
        name = os.path.splitext(filename)[0]

        await ctx.send(f'```\n[已增加 {name} 到撥放序列中]\n```', delete_after=15)

        data = {'webpage_url': None, 'title': name}

        return cls(source, data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.

        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url'],
                                          before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'),
                   data=data, requester=requester)


class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.

    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.

    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = 0.2
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'嗯....似乎沒辦法唱下去的樣子...\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source
            if self._guild.voice_client is not None:
                self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
                self.np = await self._channel.send(f'**正在撥放:** `{source.title}` 點歌者: 'f'`{source.requester}`')
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))
