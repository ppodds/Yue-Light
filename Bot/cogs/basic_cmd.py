import logging
import os
import random

import discord
from discord.ext import commands

'''Logger設置'''
logger = logging.getLogger('discord')
authorM = '<@252029078452961280>'


class BasicCmd(commands.Cog):

    def __init__(self, client):
        self.client = client

    '''
    ctx後的參數皆為指令參數
    (*,n)會把*後面所有字串當成n參數
    '''

    # 讓Bot重複字句
    @commands.command()
    async def repeat(self, ctx, *, tc=''):
        if tc != '':
            args = tc.split(' ', 1)
            if len(args) == 2:
                try:
                    times = int(args[0])
                    if not times <= 0:
                        if times <= 15:
                            await ctx.send('嘛.... 只是重複幾次的話....也不是不行喔?')
                            logger.info(f'{ctx.author}用了repeat {args[0]} {args[1]}')
                            for i in range(times):
                                await ctx.send(args[1])
                        else:
                            await ctx.send('太多次了啦! :anger:  :anger:  :anger: ')
                    else:
                        if times < 0:
                            await ctx.send('連續說負數次什麼的~ 人家不懂啦!')
                        else:
                            await ctx.send('竟然想讓人家說0次是在整人家嗎! :anger:  :anger:  :anger:')
                except ValueError as err:
                    await ctx.send('想讓人家說幾遍啦~ <:kc_arashio:502848983799169044>')
            else:
                await ctx.send('到底想讓人家重複說什麼啦~')
        else:
            await ctx.send('話不講清楚我可是不知道要做什麼的~')

    # 觀看Help
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(description="「這麼想跟Yue說話嗎? 也...也不是不可以啦~」")
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.add_field(name='和Yue聊天的方式', value='「在訊息前加上-就可以和Yue說話啦~    嘻嘻~」', inline=False)
        embed.add_field(name=':heart: :hearts: :heart: 指令清單 :heart: :hearts: :heart:',
                        value='----------------------------------------------------------', inline=False)
        embed.add_field(name='help', value='指令說明', inline=False)
        embed.add_field(name='mhelp', value='音樂指令說明', inline=False)
        embed.add_field(name='ahelp', value='助手指令說明', inline=False)
        embed.add_field(name='repeat　[次數]　[內容]', value='讓Yue大聲複誦內你說過的話', inline=False)
        embed.set_footer(text="由ppodds親手調教",
                         icon_url='https://cdn.discordapp.com/avatars/252029078452961280/27c2be84ab1ccd316241904a91b20a16.webp?size=1024')
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(BasicCmd(client))

