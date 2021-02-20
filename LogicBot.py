
import discord
from discord.ext import tasks, commands
from LDBCommands import *
import config as conf


class LogicBot(discord.Client):

    cmds = {}

    async def on_ready(self):
        self.init_cmds()
        print('Logged on as', self.user)
        print('Uid:',self.user.id)

    def init_cmds(self):
        # Init commands
        self.cmds = {'ping': CmdPing()}
        print(self.cmds['ping'].execute())
        return False

    async def on_message(self, message):
        if message in self.cmds:
            self.cmds[message].execute()
        if message.author == self.user:
            return

print(globals()['CmdPing']().execute())
LogicBot().run(conf.bot_token)
