import itertools
import logging
import os

import discord
from discord.ext import commands

from Bot.api.music import music

'''Logger設置'''
logger = logging.getLogger('discord')
authorM = '<@252029078452961280>'


class MusicCmd(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.players = {}
        self.download = False

    '''
    ctx後的參數皆為指令參數
    (*,n)會把*後面所有字串當成n參數
    '''

    # 觀看音樂相關Help
    @commands.command()
    async def mhelp(self, ctx):
        embed = discord.Embed(description="「想聽Yue唱歌嗎? 下次說不定有機會呢~~」")
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.add_field(name='和Yue聊天的方式', value='「在訊息前加上-就可以和Yue說話啦~    嘻嘻~」', inline=False)
        embed.add_field(name=':heart: :hearts: :heart: 音樂指令 :heart: :hearts: :heart:',
                        value='----------------------------------------------------------', inline=False)
        embed.add_field(name='join', value='讓Yue加入你所在的頻道', inline=False)
        embed.add_field(name='leave', value='讓Yue離開所在的頻道', inline=False)
        embed.add_field(name='play　[曲子]', value='讓Yue唱她認識的歌曲', inline=False)
        embed.add_field(name='ytplay　[Youtube Url/搜尋關鍵字]', value='讓Yue唱Youtube有的歌曲(不建議使用關鍵字 結果不一定準確)', inline=False)
        embed.add_field(name='playing', value='觀看正在撥放中的歌曲資訊', inline=False)
        embed.add_field(name='queue', value='觀看接下來幾首歌曲的順序', inline=False)
        embed.add_field(name='pause', value='讓Yue暫停唱歌', inline=False)
        embed.add_field(name='resume', value='讓Yue繼續唱歌', inline=False)
        embed.add_field(name='skip', value='讓Yue跳過當前正在唱的歌', inline=False)
        embed.add_field(name='stop', value='讓Yue離開 並清空預計要唱的歌曲', inline=False)
        embed.add_field(name='volume　[音量(0~100%)]', value='要求Yue改變唱歌音量', inline=False)
        embed.add_field(name='allsong', value='讓Yue告訴你她認識的歌曲', inline=False)
        embed.add_field(name='needdl [yes/no]', value='設定播放前是否下載音樂(若無法撥放可嘗試下載)，不加參數即顯示當前設定', inline=False)
        embed.set_footer(text="由ppodds親手調教",
                         icon_url='https://cdn.discordapp.com/avatars/252029078452961280/27c2be84ab1ccd316241904a91b20a16.webp?size=1024')
        await ctx.send(embed=embed)

    # 加入語音頻道
    @commands.command()
    @commands.guild_only()
    async def join(self, ctx):
        try:
            await self._join(ctx)
        except music.InvalidVoiceChannel:
            return

    # 加入語音頻道
    @commands.command()
    @commands.guild_only()
    async def leave(self, ctx):
        logger.info(f'{ctx.author.id} 用了leave')
        if not ctx.voice_client is None:
            await ctx.voice_client.disconnect()
            await ctx.send('好的~ 下次再見~')
        else:
            await ctx.send('嗯? 我不在你旁邊啊?')

    # 播放檔案
    @commands.command()
    @commands.guild_only()
    async def play(self, ctx, *, filename):
        await ctx.trigger_typing()

        voice_client = ctx.voice_client

        if not voice_client:
            try:
                await self._join(ctx)
            except music.InvalidVoiceChannel:
                return

        player = self.get_player(ctx)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        try:
            source = await music.YTDLSource.create_local_source(ctx, filename, loop=self.client.loop)
        except music.NoMusicFileError as err:
            return await ctx.send('Yue不認識這首歌呢...')
        await player.queue.put(source)

    # 觀看音樂檔案清單
    @commands.command()
    @commands.guild_only()
    async def allsong(self, ctx):
        # 取得所有檔案名稱並列於embed
        embed = discord.Embed(description="「Yue其實對唱歌還挺自豪的呢 <:i_yoshino:583658336054935562>」")
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.add_field(name=':heart: :hearts: :heart: 歌曲列表 :heart: :hearts: :heart:',
                        value='----------------------------------------------------------',
                        inline=False)
        embed.add_field(name='格式範例', value='「待會Yue就用這種方式照著念喔~」', inline=False)
        embed.add_field(name='編號', value='歌曲名稱', inline=False)
        embed.set_footer(text="由ppodds親手調教",
                         icon_url='https://cdn.discordapp.com/avatars/252029078452961280/27c2be84ab1ccd316241904a91b20a16.webp?size=1024')
        counte = 3
        counti = 1
        for filename in os.listdir('.\\music'):
            if counte < 25:
                embed.add_field(name=str(counti), value=filename, inline=False)
                counte += 1
                counti += 1
            else:
                await ctx.author.send(embed=embed)
                embed.clear_fields()
                embed.add_field(name=str(counti), value=filename, inline=False)
                counte = 1
                counti += 1
        await ctx.author.send(embed=embed)

    # 從Youtube搜尋歌曲並加入序列
    @commands.command(aliases=['yt'])
    @commands.guild_only()
    async def ytplay(self, ctx, *, search: str):

        await ctx.trigger_typing()

        voice_client = ctx.voice_client

        if not voice_client:
            try:
                await self._join(ctx)
            except music.InvalidVoiceChannel:
                return

        player = self.get_player(ctx)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        await music.YTDLSource.create_source(ctx, player, search, loop=self.client.loop, download=self.download)

    # 檢視即將撥放的歌曲序列
    @commands.command()
    @commands.guild_only()
    async def queue(self, ctx):
        voice_client = ctx.voice_client

        if not voice_client or not voice_client.is_connected():
            return await ctx.send('我不在你旁邊呢....', delete_after=20)

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('目前沒有歌曲在排隊中呢....')

        # 抓十個排隊中歌曲
        upcoming = list(itertools.islice(player.queue._queue, 0, 10))

        embed = discord.Embed(description="「目前已經有這麼多人和Yue點歌了呢... Yue有點小高興...」")
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.add_field(name=':heart: :hearts: :heart: 撥放序列 :heart: :hearts: :heart:',
                        value='----------------------------------------------------------', inline=False)
        embed.add_field(name=f'撥放佇列狀態',
                        value=f'目前撥放佇列中有 {player.queue.qsize()} 首歌曲', inline=False)
        embed.add_field(name='格式範例', value='「待會Yue就用這種方式照著念喔~」', inline=False)
        embed.add_field(name='順序', value='歌曲名稱', inline=False)
        embed.set_footer(text="由ppodds親手調教",
                         icon_url='https://cdn.discordapp.com/avatars/252029078452961280/27c2be84ab1ccd316241904a91b20a16.webp?size=1024')
        counti = 1
        for data in upcoming:
            embed.add_field(name=str(counti), value=data['title'], inline=False)
            counti += 1
        await ctx.send(embed=embed)

    # 觀看撥放中的歌曲資訊
    @commands.command(aliases=['np'])
    @commands.guild_only()
    async def playing(self, ctx):
        voice_client = ctx.voice_client

        if not voice_client or not voice_client.is_connected():
            return await ctx.send('我不在你旁邊呢....', delete_after=20)

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('嗯? 我沒有在唱歌喔~')

        try:
            # 移除上一個(正在撥放)的訊息
            await player.np.delete()
        except discord.HTTPException:
            pass

        player.np = await ctx.send(f'**正在撥放:** `{voice_client.source.title}` '
                                   f'點歌者: `{voice_client.source.requester}`')

    # 暫停正在撥放的曲目
    @commands.command()
    @commands.guild_only()
    async def pause(self, ctx):
        voice_client = ctx.voice_client

        if not voice_client or not voice_client.is_playing():
            return await ctx.send('嗯? 我沒有在唱歌喔~', delete_after=20)
        elif voice_client.is_paused():
            return await ctx.send('我現在已經停下來了啦 <:i_yoshino:583658336054935562>', delete_after=20)

        voice_client.pause()
        await ctx.send('那我就先停下來哦....')

    # 從暫停中恢復
    @commands.command()
    @commands.guild_only()
    async def resume(self, ctx):
        voice_client = ctx.voice_client

        if not voice_client or not voice_client.is_connected():
            return await ctx.send('嗯? 我沒有在唱歌喔~', delete_after=20)
        elif not voice_client.is_paused():
            return await ctx.send('我現在在唱歌了啦 <:i_yoshino:583658336054935562>', delete_after=20)

        voice_client.resume()
        await ctx.send('那我就繼續唱哦....')

    # 跳過當前歌曲
    @commands.command()
    @commands.guild_only()
    async def skip(self, ctx):
        voice_client = ctx.voice_client

        if not voice_client or not voice_client.is_connected():
            return await ctx.send('嗯? 我沒有在唱歌喔~', delete_after=20)

        if not voice_client.is_playing():
            return

        voice_client.stop()
        await ctx.send('欸? 不想聽這首嗎? 那好吧....')

    # 停下所有撥放歌曲並清空歌單
    @commands.command()
    @commands.guild_only()
    async def stop(self, ctx):
        voice_client = ctx.voice_client

        if not voice_client or not voice_client.is_connected():
            return await ctx.send('嗯? 我沒有在唱歌喔~', delete_after=20)
        await self.cleanup(ctx.guild)
        await ctx.send('表演結束! 下次也請多多支持!')

    # 更改音量
    @commands.command()
    @commands.guild_only()
    async def volume(self, ctx, *, volume: float):
        voice_client = ctx.voice_client

        if not voice_client or not voice_client.is_connected():
            return await ctx.send('我不在你旁邊呢....', delete_after=20)

        if not 0 < volume <= 100:
            return await ctx.send('音量要在1到100之間喔~')

        player = self.get_player(ctx)

        if voice_client.source:
            voice_client.source.volume = volume / 100

        player.volume = volume / 100
        await ctx.send(f'這樣的音量比較舒服嗎? 那我就用 {volume}% 的音量唱哦? ')

    @commands.command()
    async def needdl(self, ctx, option=''):
        if option == '':
            return await ctx.send(f'現在的設定值為:{self.download}!')
        elif option == 'yes':
            self.download = True
        elif option == 'no':
            self.download = False
        else:
            return await ctx.send('選項只能輸入yes或no!')
        await ctx.send('設定完成!')


    # 以下非指令
    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self, ctx):
        """取得屬於伺服器的music player 如果沒有就建立新物件"""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = music.MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    async def _join(self, ctx):
        if not ctx.author.voice is None:
            channel = ctx.author.voice.channel
            if not ctx.voice_client is None:
                if not ctx.voice_client.channel == channel:
                    await ctx.voice_client.move_to(channel)
                    logger.info(f'{ctx.author.id} 用了join 讓 Yue 進入了 {channel}')
                    await ctx.send('看樣子在別的地方呢.... 我去找你吧~')
                else:
                    await ctx.send('我已經在你旁邊了哦...')
            else:
                logger.info(f'{ctx.author.id} 用了join 讓 Yue 進入了 {channel}')
                await channel.connect()
                await ctx.send('我來了哦~')
        else:
            await ctx.send('看起來你不在語音頻道裡呢...')
            raise music.InvalidVoiceChannel


def setup(client):
    client.add_cog(MusicCmd(client))
