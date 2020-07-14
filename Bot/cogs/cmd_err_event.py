import logging

from discord.ext import commands
from discord.ext.commands import *

'''Logger設置'''
logger = logging.getLogger('discord')
authorM = '<@252029078452961280>'


class CmdErrEvent(commands.Cog):

    def __init__(self, client):
        self.client = client

    # on_command_error事件
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        '''
        ignored
        CommandNotFound,CommandOnCooldown,MissingPermissions,MissingRequiredArgument,NoPrivateMessage
        '''

        if isinstance(error, CommandNotFound):
            return
        elif isinstance(error, CommandOnCooldown):
            await ctx.send(f'看樣子還要{str(round(error.retry_after))}秒才能再來一次呢...')
            return
        elif isinstance(error, BotMissingPermissions):
            await ctx.send('看樣子Yue似乎沒有權限這麼做...')
            return
        elif isinstance(error, MissingRequiredArgument):
            await ctx.send('似乎漏了一些內容呢...')
            return
        elif isinstance(error, BadArgument):
            await ctx.send('似乎內容有些問題呢...')
            return
        elif isinstance(error, NoPrivateMessage):
            await ctx.send('似乎在私聊時不能做這些呢....')
            return
        elif isinstance(error, NSFWChannelRequired):
            await ctx.send('在這邊h是不可以的!')
            return
        elif isinstance(error, NotOwner):
            await ctx.send('你不是製作者呢!!')
            return
        raise error


def setup(client):
    client.add_cog(CmdErrEvent(client))
