import asyncio
import json
from typing import Literal
from discord.ext import commands
from discord import app_commands, Embed, Colour, Interaction, Message
from modules.utils import webhandler
from datetime import datetime
from collections import Counter


class Logicutils(commands.Cog, name="Logicutils"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="votetop", description="Get the top voters")
    async def votetop_command(self, interaction: Interaction):
        await interaction.response.send_message("Loading...")
        await interaction.edit_original_response(content="", embed=self.get_vote_top())

    @app_commands.command(name="serverstat", description="Server status")
    async def serverstat_command(self, interaction: Interaction, mode: Literal["compact", "full"] = "compact"):
        await interaction.response.send_message("Loading...")
        embed = Embed(title="📡 Статус", color=Colour.brand_green())
        srvsG = self.get_game_servers_status(mode)
        embed.add_field(name=srvsG.title, value=srvsG.description, inline=True)
        await interaction.edit_original_response(content="", embed=embed)
        srvsS = self.get_infrastructure_status(mode)
        embed.add_field(name=srvsS.title, value=srvsS.description, inline=True)
        await interaction.edit_original_response(content="", embed=embed)

    @app_commands.command(name="weather", description="Weather information for location")
    async def weather_command(self, interaction: Interaction, location: str, count: app_commands.Range[int, 1, 40]=3):
        data = webhandler.get_json(f"https://api.openweathermap.org/data/2.5/forecast?q={location}&cnt={count}&units=metric&appid=SUPERSECRETKEY")
        text = json.dumps(data, indent=2)
        wes = []
        for i in range(count):
            we = Embed()
            if (data['cod'] != "200"):
                we.description = f"**{data['message']}**"
                await interaction.response.send_message(embed=we)
                return
            weather = data['list'][i]
            wind = weather['wind']
            deg = wind['deg']
            text = weather['weather'][0]['description'].title()
            date = datetime.fromtimestamp(weather['dt'])
            
            #temperature
            text += "\n" + f"{weather['main']['temp_min']} — {weather['main']['temp_max']}°C"
            
            #wind
            arrows = ["↓", "↙", "←", "↖", "↑", "↗", "→", "↘"]
            type = int(((deg)%360)/45)
            text += "\n" + arrows[type] + f" {wind['speed']} — {wind['gust']} m/s"
            
            #pressure and humidity
            text += f"\n {weather['main']['pressure']} mmHg | {weather['main']['humidity']}%"
            
            
            if (count <= 10):
                #title
                we.title=f"⛅Погода ({location}) ({date.strftime('%b %d %H:%M')})"
                we.color = self.get_color_from_temperature(weather['main']['temp'])
                we.set_thumbnail(url=f"https://openweathermap.org/img/wn/{weather['weather'][0]['icon']}@4x.png")
                we.set_footer(text="OpenWeatherMap", icon_url="https://openweathermap.org/img/wn/02d.png")
                we.description = text
                wes.append(we)
            else:
                if (i == 0):  #first element
                    wem = Embed() #init multiple fields embed
                    wem.title=f"⛅Погода ({location}) ({date.strftime('%b %d')})"
                    cur_date = date
                    max_temp = 0
                    icons = [] # for count icons (and set most pupular
                if (cur_date.day != date.day):
                    wem.title=f"⛅Погода ({location}) ({cur_date.strftime('%b %d')})"
                    wem.color = self.get_color_from_temperature(max_temp)
                    wes.append(wem)
                    wem = Embed()
                    max_temp = 0
                    icons = []
                    cur_date = date
                
                wem.add_field(name=date.strftime('%H:%M'), value=text, inline=True)
                
                icons.append(weather['weather'][0]['icon'])
                
                most_pupular_icon = Counter(icons).most_common(1)[0][0]
                wem.set_thumbnail(url=f"https://openweathermap.org/img/wn/{most_pupular_icon}@4x.png")
                if (max_temp < weather['main']['temp']):
                    max_temp = weather['main']['temp']
                
                
                if (i+1 == count):
                    wem.title=f"⛅Погода ({location}) ({date.strftime('%b %d')})"
                    wem.color = self.get_color_from_temperature(max_temp)
                    wem.set_footer(text="OpenWeatherMap", icon_url="https://openweathermap.org/img/wn/02d.png")
                    wes.append(wem)

        await interaction.response.send_message(embeds=wes)

    def get_color_from_temperature(self, temperature) -> Colour:
        # Determination of the temperature range and corresponding colors
        color_ranges = [
            {'temperature': -20, 'color': '0000FF'},  # Blue
            {'temperature': 0, 'color': '00FFFF'},   # light blue
            {'temperature': 10, 'color': '00FF00'},   # Green
            {'temperature': 20, 'color': 'FFFF00'},   # Yellow
            {'temperature': 30, 'color': 'FF0000'},   # Red
        ]
        
        # Search for the corresponding color for a given temperature
        for i in range(len(color_ranges)):
            if temperature < color_ranges[i]['temperature']:
                if i == 0:
                    return color_ranges[i]['color']
                else:
                    # Linear interpolation between the two nearest colors
                    prev_temp = color_ranges[i-1]['temperature']
                    prev_color = color_ranges[i-1]['color']
                    next_temp = color_ranges[i]['temperature']
                    next_color = color_ranges[i]['color']
                    ratio = (temperature - prev_temp) / (next_temp - prev_temp)
                    
                    # Calculation of an intermediate color
                    r = int((1 - ratio) * int(prev_color[0:2], 16) + ratio * int(next_color[0:2], 16))
                    g = int((1 - ratio) * int(prev_color[2:4], 16) + ratio * int(next_color[2:4], 16))
                    b = int((1 - ratio) * int(prev_color[4:6], 16) + ratio * int(next_color[4:6], 16))
                    
                    hex_color = '{:02X}{:02X}{:02X}'.format(r, g, b)
                    
                    return Colour(int(hex_color, 16))
        
        # If temp very hot - return latest
        return Colour(int(color_ranges[-1]['color'], 16))  
        
    def get_color_from_temperature2(self, temperature):
        color_ranges = [
            (-20, Colour.dark_blue()),    # Blue
            (0, Colour.blue()),   # Light blue
            (10, Colour.green()),   # Green
            (20, Colour.yellow()),   # Yellow
            (30, Colour.red())    # Red
        ]
        
        for temp, color in color_ranges:
            if temperature < temp:
                return color
        
        return color_ranges[-1][1]

    @app_commands.command(name="hardware", description="User hardware information")
    async def hardware_command(self, interaction: Interaction, user: str):
        data = webhandler.get_json(f"https://logixy.net/launcher/profileapi.php?mode=hw&user={user}")
        data_avatar = webhandler.get_json(f"https://logixy.net/launcher/profileapi.php?mode=avatar&user={user}")
        #text = json.dumps(data, indent=2)
        text = f"GPU: **{data['gpu']}**\nRAM: **{data['ram']}GB**\nCPU: **{data['physicalProcessors']} cores {data['logicalProcessors']} threads | {data['processorMaxFreq']}Ghz**"
        embed = Embed(title=f"{user}`s hardware", description=text, color=Colour.brand_red())
        embed.set_thumbnail(url=f"https://logixy.net{data_avatar['url']}")
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="user", description="User information")
    async def user_command(self, interaction: Interaction, user: str):
        data = webhandler.get_json(f"https://logixy.net/launcher/profileapi.php?mode=user&user={user}")
        data_avatar = webhandler.get_json(f"https://logixy.net/launcher/profileapi.php?mode=avatar&user={user}")
        #text = json.dumps(data, indent=2)
        text = ""
        for key in data:
            text = text + f"**{key}**: {data[key]}\n"
        embed = Embed(title=f"{user}`s info", description=text, color=Colour.brand_red())
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

    def get_game_servers_status(self, mode) -> Embed:
        spisok = webhandler.get_json('https://logixy.net/monAJAX/cache/cache.json')
        title = "🎮 Игровые серверы"
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
                    progressbar_size = 6
                    progress = round((s_data['online'])/(s_data['slots'])*100)
                    curr_progress_val = progressbar_size*progress//100
                    text_progress_bar = ("█"*curr_progress_val).ljust(progressbar_size, "░")
                    if (mode == 'compact'):
                        text += f"{stat_e}**{s_name}** [{s_data['online']}/{s_data['slots']}]\n"
                    else:
                        text += stat_e + "**" + s_name + f"** [{text_progress_bar}] (" + str(s_data['online']) + "/" + str(
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
    
    def get_infrastructure_status(self, mode) -> Embed:
        title = "⚙️ Оборудование"
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
