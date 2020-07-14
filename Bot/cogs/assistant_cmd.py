import logging

import discord
from discord.ext import commands

'''Logger設置'''
logger = logging.getLogger('discord')
authorM = '<@252029078452961280>'


class AssistantCmd(commands.Cog):

    def __init__(self, client):
        self.client = client

    '''
    ctx後的參數皆為指令參數
    (*,n)會把*後面所有字串當成n參數
    '''

    # 觀看助手Help
    @commands.command()
    async def ahelp(self, ctx):
        embed = discord.Embed(description="「有些事情 Yue是指跟喜歡的人才做喔~ :heart:」")
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.add_field(name='gu　[使用者ID]', value='讓Yue幫忙查找使用者', inline=False)
        embed.add_field(name='roles　[使用者ID]', value='讓Yue幫忙查找使用者的所有身分組', inline=False)
        embed.set_footer(text="由ppodds親手調教",
                         icon_url='https://cdn.discordapp.com/avatars/252029078452961280/27c2be84ab1ccd316241904a91b20a16.webp?size=1024')
        await ctx.send(embed=embed)

    # 利用user ID取得名稱
    @commands.command()
    async def gu(self, ctx, id: discord.User):
        try:
            await ctx.send(f'這個人的名字是 {id.name} 的樣子...')
            logger.info(f'{ctx.author.id}(user) 用了gu  id；{id}')
        except:
            await ctx.send(f'找不到這個人的樣子...是不是你弄錯了?')

    # 利用user ID取得身分組列表(物件)
    @commands.command()
    async def roles(self, ctx, id: discord.Member):
        try:
            await ctx.send(f'這個人的身分組有： {id.roles} ')
            logger.info(f'{ctx.author.id}(user) 用了roles  id；{id}')
        except:
            await ctx.send(f'找不到這個人的樣子...是不是你弄錯了?')


# 以下非指令
def setup(client):
    client.add_cog(AssistantCmd(client))
