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
                    text += stat_e + "**" + s_name + "** - (" + str(s_data['online']) + "/" + str(
                        s_data['slots']) + ") (" + str(s_data['ping']) + "ms)\n"
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