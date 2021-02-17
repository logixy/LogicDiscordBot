
import discord
from discord.ext import tasks, commands
from commands import *
import config as conf


class LogicBot(discord.Client):

    cmds = {}

    async def on_ready(self):
        self.init_cmds()
        print('Logged on as', self.user)
        print('Uid:',self.user.id)

    def init_cmds(self):
        # Init commands
        #self.cmds = {'ping': CmdPing()}
        print(CmdPing().execute())
        return

    async def on_message(self, message):
        if message.author == self.user:
            return

LogicBot().run(conf.bot_token)
