
from commands.Command import Command


class CmdPing(Command):

    def execute(self):
        return 'Pong!'

    def name(self):
        return self.command
