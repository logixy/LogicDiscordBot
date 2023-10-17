from discord.ext import commands
from discord import app_commands, Embed, Colour, Interaction
from modules.utils import brainfuck


class Brainfuck(commands.Cog, name="Brainfuck"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bf", description="Brainfuck interpretator")
    async def bf_command(self, interraction: Interaction, code: str):
        result = brainfuck.run(code)
        embed = Embed(
          title="🧾 Brainfuck interpretation",
          description=result,
          colour=Colour.yellow())
        await interraction.response.send_message(embed=embed)

    @app_commands.command(name="bft", description="Brainfuck translator")
    async def tbf_command(self, interraction: Interaction, string: str):
        result = brainfuck.string_to_bf(string, False)
        embed = Embed(
          title="📖 Brainfuck translation",
          description=result,
          colour=Colour.yellow())
        await interraction.response.send_message(embed=embed)




async def setup(bot):
    await bot.add_cog(Brainfuck(bot))