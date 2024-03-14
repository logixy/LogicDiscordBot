import asyncio
import json
from discord.ext import commands
from discord import app_commands, Embed, Colour, Interaction, Message
from modules.utils import webhandler


class Logicutils(commands.Cog, name="Logicutils"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="votetop", description="Get the top voters")
    async def votetop_command(self, interaction: Interaction):
        await interaction.response.send_message("Loading...")
        await interaction.edit_original_response(content="", embed=self.get_vote_top())

    @app_commands.command(name="serverstat", description="Server status")
    async def serverstat_command(self, interaction: Interaction):
        await interaction.response.send_message("Loading...")
        await interaction.edit_original_response(content="", embeds=[self.get_game_servers_status(),
                                                   self.get_infrastructure_status()])
    
    @app_commands.command(name="weather", description="Weather information for location")
    async def weather_command(self, interaction: Interaction, location: str):
        data = webhandler.get_json(f"https://api.openweathermap.org/data/2.5/forecast?q={location}&cnt=1&units=metric&appid=SUPERSECRETKEY")
        text = json.dumps(data, indent=2)
        we = Embed(title=f"⛅Погода ({location})", color=Colour.blue())
        if (data['cod'] != "200"):
            we.description = f"**{data['message']}**"
            await interaction.response.send_message(embed=we)
            return
        weather = data['list'][0]
        wind = weather['wind']
        deg = wind['deg']
        text = weather['weather'][0]['description'].title()
        
        #temperature
        text += "\n" + f"{weather['main']['temp_min']} - {weather['main']['temp_max']}°C"

        #wind
        arrows = ["↓", "↙", "←", "↖", "↑", "↗", "→", "↘"]
        type = round(((deg+22)%360)/45)
        text += "\n" + arrows[type] + f" {wind['speed']} — {wind['gust']} m/s"

        #pressure and humidity
        text += f"\n {weather['main']['pressure']} mmHg | {weather['main']['humidity']}%"
        
        we.set_thumbnail(url=f"https://openweathermap.org/img/wn/{weather['weather'][0]['icon']}@4x.png")
        
        we.description = text

        we.set_footer(text="OpenWeatherMap", icon_url="https://openweathermap.org/img/wn/02d.png")
        await interaction.response.send_message(embed=we)

        

    @app_commands.command(name="hardware", description="User hardware information")
    async def hardware_command(self, interaction: Interaction, user: str):
        data = webhandler.get_json(f"https://logixy.net/launcher/profileapi.php?mode=hw&user={user}")
        data_avatar = webhandler.get_json(f"https://logixy.net/launcher/profileapi.php?mode=avatar&user={user}")
        #text = json.dumps(data, indent=2)
        text = f"GPU: **{data['gpu']}**\nRAM: **{data['ram']}GB**\nCPU: **{data['physicalProcessors']} cores {data['logicalProcessors']} threads | {data['processorMaxFreq']}Ghz**"
        embed = Embed(title=f"{user}`s hardware", description=text, color=Colour.brand_red())
        embed.set_thumbnail(url=f"https://logixy.net{data_avatar['url']}")
        await interaction.response.send_message(embed=embed)
    
    def get_vote_top(self) -> Embed:
        spisok = webhandler.get_json(
            'https://logixy.net/launcher/tableTopVote.php?mode=api')
        title = "🏆 Топ голосующих"
        if(spisok is False):
            text = 'Ошибка соединения с API: ' + webhandler.req_error
        else:
            text = ""
            i = 0
            for userdata in spisok:
                text += f"**{str(i + 1)}** . **" + userdata['user'].replace('_', '\\_').title(
                ) + "** - **" + userdata['ammount'] + "**\n"
                i += 1
        return Embed(title=title, description=text, color=Colour.brand_green())

    def get_game_servers_status(self) -> Embed:
        spisok = webhandler.get_json('https://logixy.net/monAJAX/cache/cache.json')
        title = "🎮 Статус игровых серверов"
        if(spisok is False):
            text = 'Ошибка соединения API проверки статусов игровых серверов: ' + webhandler.req_error
        else:
            text = ''
            for s_name in spisok['servers']:
                s_data = spisok['servers'][s_name]
                if (s_data['status'] == 'online'):
                    stat_e = ':green_circle:'
                    if (s_data['ping'] > 300):
                        stat_e = ':yellow_circle:'
                    if (s_data['ping'] > 350):
                        stat_e = ':orange_circle:'
                    if (s_data['ping'] > 450):
                        stat_e = ':brown_circle:'
                    # Progressbar
                    progressbar_size = 20
                    progress = round((s_data['online'])/(s_data['slots'])*100)
                    curr_progress_val = progressbar_size*progress//100
                    text_progress_bar = ("█"*curr_progress_val).ljust(progressbar_size, "░")
                    text += stat_e + "**" + s_name + f"** \n [{text_progress_bar}] (" + str(s_data['online']) + "/" + str(
                        s_data['slots']) + ")\n"
                else:
                    text += ":red_circle:**" + s_name + \
                        "** - (**" + s_data['status'] + "**)" + "\n"
            text += "\n**Общий онлайн:** " + \
                str(spisok['online']) + "/" + str(spisok['slots']) + "\n"
            text += "**Рекорд дня:** " + \
                str(spisok['recordday']) + \
                " (" + spisok['timerecday'] + ")\n"
            text += "**Рекорд:** " + \
                str(spisok['record']) + " (" + spisok['timerec'] + ")\n"
        return Embed(title=title, description=text, color=Colour.brand_green())
    
    def get_infrastructure_status(self) -> Embed:
        title = "⚙️ Статус серверного оборудования"
        servers_stats = webhandler.get_json('https://status.logixy.net/api')
        errors_data = {
            'Server \#1': 'Недоступен сервер #1! Cкорее всего нет энергообеспечения либо интернет-соединения.',
            'CDN': 'Недоступен главный CDN. Может наблюдаться низкая скорость скачивания и обновления игровых клиентов.',
            'Server \#2': 'Недоступен сервер #2! Cкорее всего нет энергообеспечения либо интернет-соединения.',
            'Radio': 'Наблюдаются проблемы с радио-сервером. Придется посидеть в тишине. Его вообще кто-то слушает?!',
            'Launch-server': 'На данный момент лаунч-сервер не доступен. Весь функционал лаунчера недоступен.'
        }
        err_data = ''
        text = ''
        for server in servers_stats:
            if (server['available'] != 'Online'):
                stat_e = ':red_circle:'
                if (server['name'] in errors_data):
                    err_data += ":exclamation: " + errors_data[server['name']] + "\n"
            else:
                stat_e = ':green_circle:'
            text += stat_e + "**" + \
                server['name'] + "** - " + server['available'] + "\n"
        text += "\n" + err_data + "\nСтраница мониторинга проекта <https://status.logixy.net/>"
        return Embed(title=title, description=text, color=Colour.brand_green())
    
    @commands.Cog.listener("on_message")
    async def chat_message(self, message: Message):
        if (message.author.bot):
            return
        
        message_text = message.content
        lowered_message = message_text.lower()

        if lowered_message in ['топ голосующих', 'топ голосов', 'топ голосовавших']: 
            await message.reply(embed=self.get_vote_top())

        if lowered_message in ['статуссерверов', 'статус серверов', 'статус сервера', 'server stat', 'статистика сервера']:
            await message.reply(embeds=[self.get_game_servers_status(),
                                       self.get_infrastructure_status()])

async def setup(bot):
    await bot.add_cog(Logicutils(bot))