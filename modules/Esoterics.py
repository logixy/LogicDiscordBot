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
        moon_icon = {
            'moon_day_1':  '🌑',
            'moon_day_2':  '🌒',
            'moon_day_3':  '🌒',
            'moon_day_4':  '🌒',
            'moon_day_5':  '🌒',
            'moon_day_6':  '🌒',
            'moon_day_7':  '🌒',
            'moon_day_8':  '🌓',
            'moon_day_9':  '🌓',
            'moon_day_10': '🌓',
            'moon_day_11': '🌔',
            'moon_day_12': '🌔',
            'moon_day_13': '🌔',
            'moon_day_14': '🌔',
            'moon_day_15': '🌔',
            'moon_day_16': '🌕',
            'moon_day_17': '🌖',
            'moon_day_18': '🌖',
            'moon_day_19': '🌖',
            'moon_day_20': '🌖',
            'moon_day_21': '🌖',
            'moon_day_22': '🌗',
            'moon_day_23': '🌗',
            'moon_day_24': '🌗',
            'moon_day_25': '🌘',
            'moon_day_26': '🌘',
            'moon_day_27': '🌘',
            'moon_day_28': '🌘',
            'moon_day_29': '🌘',
            'moon_day_30': '🌑'
        }
        data = webhandler.get_json(f"https://horoscopes.rambler.ru/api/front/v4/moon/widget/")
        embed = Embed(
          title="🌙 Лунный календарь",
          description=moon_icon[data['icon']] + " " + data['title'],
          colour=Colour.dark_purple(),
          timestamp=datetime.datetime.now())
        await interaction.response.send_message(embed=embed) # , delete_after=60
        data = webhandler.get_json(f"https://horoscopes.rambler.ru/api/front/v4/hair/status/today/")
        hair = "Удачный день для стрижки" if data['status'] == 'lucky' else "Неудачный день для стрижки"
        embed.description += "\n✂️ " + hair
        await interaction.edit_original_response(embed=embed)

async def setup(bot):
    await bot.add_cog(Esoterics(bot))