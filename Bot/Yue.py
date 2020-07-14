import logging
import os
import random

import discord
from discord.ext import commands, tasks

'''Logger設置'''
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = commands.Bot(command_prefix='-', owner_id=252029078452961280)

'''更改Bot狀態'''


@tasks.loop(minutes=1)
async def change_presence_task():
    await client.wait_until_ready()
    with open('.\\bot\\data\\statusList', 'r', encoding='UTF-8') as f:
        status_list = f.readlines()
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(status_list)))


'''Bot登入後的簡單處理'''


@client.event
async def on_connect():
    # 檢查檔案完整性
    dir_init()


@client.event
async def on_ready():
    print('登入成功')
    print('Bot名稱： {0}'.format(client.user.name))
    print('------')


'''清除預設help指令'''
client.remove_command('help')
'''啟動Loop Task'''
change_presence_task.start()
'''載入cog'''
for filename in os.listdir('.\\bot\\cogs'):
    if filename.endswith('.py'):
        '''[:-3]去掉檔案的.py副檔名'''
        client.load_extension(f'cogs.{filename[:-3]}')

'''檔案資料夾初始化'''


def dir_init():
    '''檢查資料夾是否存在'''
    music = '.\\music'
    os.makedirs(music, exist_ok=True)
with open('.\\bot\\data\\token', 'r', encoding='UTF-8') as f:
    token = f.readline()
'''啟動程式上線'''
client.run(token)
