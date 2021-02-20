
from LDBCommands.LDBCommand import LDBCommand


class CmdPing(LDBCommand):

    def execute(self):
        return 'Pong!'

    def name(self):
        return self.command
