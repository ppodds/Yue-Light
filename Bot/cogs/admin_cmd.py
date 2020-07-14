import asyncio
import logging
import os
import shutil
import threading
import typing
from datetime import datetime, timedelta

import discord
from discord.ext import commands


class AdminCmd(commands.Cog):

    def __init__(self, client):
        self.client = client

    # 加身分組
    @commands.command()
    @commands.bot_has_permissions(manage_roles=False)
    @commands.is_owner()
    async def ar(self, ctx, member: discord.Member, role_id: discord.Role):
        await member.add_roles(role_id)
        await ctx.send(f'已添加 {role_id.name} 給 {member.display_name}')

    # 讓Bot私訊目標
    @commands.is_owner()
    @commands.command()
    async def msg(self, ctx, receiver: typing.Union[discord.User, discord.TextChannel, discord.Role], *,
                  content=''):
        if content != '':
            await ctx.channel.purge(limit=1, check=lambda m: m.author == ctx.author)
            if not isinstance(receiver, discord.Role):
                await receiver.send(content)
            else:
                for user in receiver.members:
                    await user.send(content)
        else:
            await ctx.send('嗯.... 這樣不太對呢!? 話要好好說清楚的呦~')

    # 關閉Bot
    @commands.command()
    @commands.is_owner()
    async def bye(self, ctx):
        await ctx.send('那就到這邊了.... 下次再見吧....')
        await self.client.close()
def setup(client):
    client.add_cog(AdminCmd(client))
