import datetime
from typing import Literal
from discord.ext import commands
from discord import app_commands, Embed, Colour, Interaction
from modules.utils import webhandler


class Esoterics(commands.Cog, name="Esoterics"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name = "horoscope", description = "Get a horoscope today.")
    async def horoscope_command(self, interaction: Interaction,
        sign: Literal["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]):
        data = webhandler.get_json(f"https://horoscopes.rambler.ru/api/front/v1/horoscope/today/{sign}/")
        embed = Embed(
          title="☯️ "+data['h1'],
          description=data['text'],
          colour=Colour.dark_purple(),
          timestamp=datetime.datetime.now())
        embed.set_footer(text=data['seo_text'])
        await interaction.response.send_message(embed=embed) # , delete_after=60

    @app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name = "lunarday", description = "Lunar day for today.")
    async def lunarday_command(self, interaction: Interaction):
        data = webhandler.get_json(f"https://horoscopes.rambler.ru/api/front/v4/moon/widget/")
        embed = Embed(
          title="🌖 Лунный календарь",
          description=data['title'],
          colour=Colour.dark_purple(),
          timestamp=datetime.datetime.now())
        await interaction.response.send_message(embed=embed) # , delete_after=60

async def setup(bot):
    await bot.add_cog(Esoterics(bot))