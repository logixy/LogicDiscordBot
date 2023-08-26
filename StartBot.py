import discord
from discord import app_commands
import requests
import json
import random
import urllib
from requests.exceptions import Timeout
from discord.ext import tasks, commands
from discord.utils import get
import config as conf
from ProjectEverydayLogo import MakePerfect as mpi
import brainfuck as bf
from fake_useragent import UserAgent
import time
import yt_dlp
import ytmusicapi
import os
import uuid
import asyncio
from transliterate import slugify

class MyClient(discord.Client):
    req_error = ''

    async def on_ready(self):
        print('Logged on as', self.user)
        print('Uid:', self.user.id)
        await tree.sync()

        file_guild_id = open("server_gen_id.txt", "r").read()
        if file_guild_id != "":
            self.avserverId = self.get_guild(
                    int(file_guild_id))
            self.gen_rand_avatar.start()

    def get_from(self, url):
        headers = {'X-Requested-With': 'XMLHttpRequest',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'}
        try:
            req = requests.get(url, headers=headers, timeout=20)
        except Timeout:
            return False
        else:
            return json.loads(req.text)

    def gen_rand_word(self, type):  # type 2 - adjective (прилагать.) 1 - noun (сущ.)
        #req = self.get_from(
        #    'http://free-generator.ru/generator.php?action=word&type=' + str(type))
        #if(req == False):
        #    return 'Ошибка соединения с API: ' + self.req_error

        #return req['word']['word']
        if(type == 2):
            lines = list(open('adjectives.txt', encoding="utf8"))
        else:
            lines = list(open('nouns.txt', encoding="utf8"))
        return random.choice(lines).strip()

    avserverId = None

    @tasks.loop(minutes=30)
    async def gen_rand_avatar(self):
        if self.avserverId != None:
            try:
                mpi.generateIcon(drawModeRandom=False, drawMode=1, drawTextMode=1)
                with open('ProjectEverydayLogo/out/out.png', 'rb') as f:
                    icon = f.read()
                await self.avserverId.edit(icon=icon)
            except Exception as error:
                print(error)

    def convert_qwe_message(self, txt):
        qwe = list("qwertyuiop[]asdfghjkl;'zxcvbnm,./")
        conv_qwe = list("йцукенгшщзхъфывапролджэячсмитьбю.")
        txt = list(txt)
        for i in range(len(txt)):
            for j in range(len(qwe)):
                if txt[i] == qwe[j]:
                    txt[i] = conv_qwe[j]
        return ''.join(txt)

    def upper_case_random_chars(self, string):
        result = ""
        for char in string:
            if random.choice([True, False]):
                result += char.upper()
            else:
                result += char
        return result

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        message.content = message.content.lower()
        original_layout_command = message.content
        # Перевод сообщения написанного в английской раскладке
        if len(message.content) > 0:
                if not (message.content[0] in "йцукенгшщзхъфывапролджэячсмитьбю"):
                        message.content = self.convert_qwe_message(message.content)
        # print(message.content)
        if(message.content == '<@!' + str(self.user.id) + '>'):
            text = 'Что Вам необходимо?\n ' + \
                '**Доступные команды на данный момент:** \n' + \
                '<@!' + str(self.user.id) + '> - Вызвать данную подсказку\n' + \
                '`Cмени аву плз` - Смена аватара сервера на случайно сгенерированный\n' + \
                '    Алисы: `смени аватар сервера`, `смени иконку сервера`, `смени иконку плз`\n' + \
                '`Бип` - Послать ботов\n' + \
                '    Алисы: `боп`, `буп`\n' + \
                '`Шуткани` -  Случайная шутка\n' + \
                '    Алисы: `пошути`, `анекдот`\n' + \
                '`Факт` - Случайный факт\n' + \
                '    Алисы: `истина`\n' + \
                '`Топ голосующих` - Вывести топ голосующих на текущий момент\n' + \
                '    Алисы: `топ голосов`, `топ голосовавших`\n' + \
                '`Статус серверов` - Узнать статус игровых серверов\n' + \
                '    Алисы: `статус сервера`, `server stat`, `статистика сервера`\n' + \
                '`Кто я?` - Узнать кто ты есть на самом деле\n' + \
                '    Алисы: `кто я есть?`, `кто же я?`, `ну кто же я?`, `божечки, что я такое?!`\n' + \
                '`Кто ты?` - Кто же он?\n' + \
                '    Алисы: `кто он?`, `кто же он?`, `кто же ты?`\n' + \
                '`Получится?` - Перед тем как что-то сделать спроси, а получится ли у тебя?\n' + \
                '    Алисы: `получилось?`, `вышло?`, `выйдет?`\n' + \
                '`Пинг` - Понг!\n' + \
                '    Алисы: `ping`, `пинг!`, `ping!`\n' + \
                '`Смени мне никнейм` - Если вы хотите получить новую личность в нашем самопровозглашенном государстве\n' + \
                '    Алисы: `смени мне ник`, `смени мой ник`, `измени мой ник`\n' + \
                '`Cбрось мой ник` - Вернутся к прошлой жизни и забыть все невзгоды.\n' + \
                '    Алисы: `сбрось мне ник`, `скинь мой ник`\n' + \
                '`Задай тему разговора` -  Вам не о чем поболтать? Попросите подсказать тему. у бота.\n' + \
                '    Алисы: `давай новую тему разговора`\n' + \
                '`Где я?` - Если вы вдруг потерялись, можете спросить прохожего бота для уточнения своего местоположения.\n' + \
                '    Алисы: `где я оказался?`, `где же я?`, `где я нахожусь?`, `где я сейчас?`, `где я сейчас нахожусь?`\n'
            await message.reply(text)

        if len(message.content) == message.content.upper().count("А") and len(message.content) > 2:
            sta = "а" * random.randint(10, 30)
            await message.reply(self.upper_case_random_chars(sta))

        if message.content in ['бип', 'боп', 'буп']:
            await message.reply(random.choice(['Бип', 'Боп', 'Буп', 'null', 'undefined', 'out of bounds', 'себе по'+message.content+'ай', \
            'Я в своем познании настолько преисполнился что я как будто бы уже сто триллионов миллиардов лет проживаю на триллионах и триллионах таких же планет, понимаешь как эта земля.']))

        if message.content in ['запусти автогенерацию аватарки']:
            if not(message.author.guild_permissions.administrator):
                await message.channel.send(self.gen_rand_word(2).title() + ', у вас нет доступа к этой комманде 😥')
                return
            print(self.avserverId, message.guild.id)
            self.avserverId = self.get_guild(
                int(message.guild.id))
            print(self.avserverId, message.guild.id)
            if not self.gen_rand_avatar.is_running():
                file_guild_id = open("server_gen_id.txt", "w")
                file_guild_id.write(str(message.guild.id))
                self.gen_rand_avatar.start()
                await message.reply('Запущена авто-генерация аватарки каждые 30 минут.')
            else:
                await message.reply('Генерация уже запущена.')
        if message.content in ['останови автогенерацию аватарки']:
            if not(message.author.guild_permissions.administrator):
                await message.channel.send(self.gen_rand_word(2).title() + ', у вас нет доступа к этой комманде 😥')
                return
            file_guild_id = open("server_gen_id.txt", "w")
            file_guild_id.write("")
            self.gen_rand_avatar.stop()
            await message.reply('Авто-генерация аватарки каждые 30 минут - будет отключена при следующей итерации генерирования.')

        if message.content in ['смени аву плз', 'смени аватар сервера', 'смени иконку сервера', 'смени иконку плз', 'смени лого сервера', 'смени лого']:
            if not(message.author.guild_permissions.administrator):
                await message.channel.send(self.gen_rand_word(2).title() + ', у вас нет доступа к этой комманде 😥')
                return
            if(message.guild == None):
                await message.channel.send('Данную команду можно использовать только на сервере!')
                return
            m2 = ['Передаю вашу заявку нашему художнику...', 'Снижаем ЗП дизайнера...', 'Вызываем омон в дом художника...',
                  'Вежливо уговариваем художника...', 'Под пытками заставляем нашего дизайнера...']
            await message.reply('Принято! ' + random.choice(m2))
            mpi.generateIcon(drawModeRandom=False, drawMode=1, drawTextMode=1)
            server = self.get_guild(int(message.guild.id))

            with open('ProjectEverydayLogo/out/out.png', 'rb') as f:
                icon = f.read()
            await server.edit(icon=icon)
            await message.reply('Готово!')
        if message.content in ['шуткани', 'пошути', 'анекдот']:
            req = self.get_from('https://randstuff.ru/joke/generate/')
            if(req == False):
                await message.reply('Ошибка соединения с API: ' + self.req_error)
                return
            await message.channel.send(req['joke']['text'])
        if message.content in ['факт', 'истина']:
            req = self.get_from('https://randstuff.ru/fact/generate/')
            if(req == False):
                await message.reply('Ошибка соединения с API: ' + self.req_error)
                return
            await message.channel.send(req['fact']['text'])
        if message.content in ['топ голосующих', 'топ голосов', 'топ голосовавших']:
            spisok = self.get_from(
                'https://logicworld.ru/launcher/tableTopVote.php?mode=api')
            if(spisok == False):
                await message.reply('Ошибка соединения с API: ' + self.req_error)
                return
            text = "На текущий момент топ голосующих такой:\n"
            i = 0
            for userdata in spisok:
                static_text = " - **" + userdata['user'].replace('_', '\\_').title(
                ) + "** Счёт - **" + userdata['ammount'] + "** Доп. голоса - **" + userdata['cheatAmmount'] + "**\n"
                text += str(i + 1) + static_text
                i += 1
            await message.reply(text)
        if message.content in ['статуссерверов', 'статус серверов', 'статус сервера', 'server stat', 'статистика сервера']:
            spisok = self.get_from('https://logicworld.ru/monAJAX/cache/cache.json')
            if(spisok == False):
                await message.reply('Ошибка соединения с API проверки статусов игровых серверов: ' + self.req_error)
            else:
                text = "Статус игровых серверов:\n"
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
                await message.reply(text)
            text = "**Статус серверного оборудования:**\n"
            servers_stats = self.get_from('https://status.logicworld.ru/api')
            errors_data = {
                'Server \#1': 'Недоступен сервер #1! Cкорее всего нет энергообеспечения либо интернет-соединения.',
                'CDN': 'Недоступен главный CDN. Может наблюдаться низкая скорость скачивания и обновления игровых клиентов.',
                'Server \#2': 'Недоступен сервер #2! Cкорее всего нет энергообеспечения либо интернет-соединения.',
                'Radio': 'Наблюдаются проблемы с радио-сервером. Придется посидеть в тишине. Его вообще кто-то слушает?!',
                'Launch-server': 'На данный момент лаунч-сервер не доступен. Весь функционал лаунчера недоступен.'
            }
            err_data = ''
            for server in servers_stats:
                if (server['available'] != 'Online'):
                    stat_e = ':red_circle:'
                    if (server['name'] in errors_data):
                        err_data += ":exclamation: " + errors_data[server['name']] + "\n";
                else:
                    stat_e = ':green_circle:'
                text += stat_e + "**" + \
                    server['name'] + "** - " + server['available'] + "\n"
            text += "\n" + err_data + "\nСтраница мониторинга проекта <https://status.logicworld.ru/>"
            await message.reply(text)
        if message.content in ['дайденег', 'дай деняг', 'деняг дай', 'дай денег', 'денег дай', 'выдай денег', 'пшму ьу ьщтун']:
            await message.reply("Держи $" + str(random.randrange(1,12)))
        if message.content in ['ктоя?', 'кто я?', 'кто я есть?', 'кто же я?', 'ну кто же я?', 'божечки, что я такое?!', 'хто я?']:
            await message.reply("Ты - " + self.gen_rand_word(1) + ".")
        if message.content in ['кто?', 'кто она?', 'хто она?', 'кто ты?', 'кто он?', 'кто же он?', 'кто же ты?', 'хто он?', 'хто же он?', 'хто ты?']:
            await message.reply("Я думаю, он - " + self.gen_rand_word(1) + ".")
        if message.content in ['почему я?', 'почему он?', 'почему они?', 'почему мы?', 'почему она?', 'почему?']:
            await message.reply("Потому что " + self.gen_rand_word(1) + ".")
        if message.content in ['где?', 'где он?', 'где она?', 'где я?', 'где я оказался?', 'где же я?', 'где я нахожусь?', 'где я сейчас?', 'где я сейчас нахожусь?']:
            req = self.get_from('https://randstuff.ru/city/generate/')
            await message.reply("Я думаю, в городе " + req['city']['city'] + " (" + req['city']['country'] + ").")
        if message.content in ['делать?', 'строить?', 'b8', 'получится?', 'получилось?', 'вышло?', 'выйдет?']:
            answ8 = ['Бесспорно', 'Предрешено', 'Никаких сомнений', 'Определённо да',
                     'Можешь быть уверен в этом', 'Мне кажется — «да»', 'Вероятнее всего',
                     'Хорошие перспективы', 'Знаки говорят — «да»', 'Да',
                     'Пока не ясно, попробуй снова', 'Спроси позже', 'Лучше не рассказывать',
                     'Сейчас нельзя предсказать', 'Сконцентрируйся и спроси опять',
                     'Даже не думай', 'Мой ответ — «нет»', 'По моим данным — «нет»',
                     'Перспективы не очень хорошие', 'Весьма сомнительно']
            emojies = [':smiling_face_with_3_hearts:', ':sweat_smile:', ':sunglasses:',
                       ':upside_down:', ':point_up:', ':thinking:', ':woman_shrugging:', ':face_with_raised_eyebrow:',
                       ':eyes:', ':woman_gesturing_no:', ':dancer:', ':no_mouth:']
            await message.reply(random.choice(answ8).lower() + " " + random.choice(emojies))
        if message.content in ['пинг', 'ping', 'пинг!', 'ping!']:
            await message.reply('Понг!')
        if message.content in ['сменимненик', 'смени мне никнейм', 'смени мне ник', 'смени мой ник', 'измени мой ник']:
            if(message.guild == None):
                await message.channel.send('Данную команду можно использовать только на сервере!')
                return
            await message.channel.send('Печатаем новый паспорт...')
            '''
            req = self.get_from(
                'http://free-generator.ru/generator.php?action=word&type=2')
            if(req == False):
                await message.reply('Ошибка соединения с API: ' + self.req_error)
                return
            req2 = self.get_from(
                'http://free-generator.ru/generator.php?action=word&type=1')
            profession = json.loads(requests.post(
                'https://randomall.ru/api/general/jobs').text)
            if(req2 == False or profession == False):
                await message.reply('Ошибка соединения с API: ' + self.req_error)
                return
            '''
            if random.choice([True, False, False, False]):
                newNick = self.gen_rand_word(2).title() + " " + \
                    self.gen_rand_word(1).title()
            else:
                randNicks = json.loads(requests.post('https://plarium.com/services/api/nicknames/new/create?group=2&gender=2').text)
                newNick = random.choice(randNicks)
            try:
                await message.author.edit(nick=newNick)
            except:
                msg = 'Мы подобрали Вам новое имя: **' + newNick + '**\n' + \
                    'Но, службы свыше запретили нам вмешиватся. Так что сменить данные вы можете вручную.'
                await message.reply(msg)
            else:
                msg = 'Добро пожаловать, **' + newNick + '**, которого мы никогда не видели :face_with_hand_over_mouth:\n'
                await message.channel.send(msg)
        if message.content in ['сбрось мой ник', 'сбрось мне ник', 'скинь мой ник']:
            if(message.guild == None):
                await message.reply('Данную команду можно использовать только на сервере!')
                return
            try:
                await message.author.edit(nick=None)
            except:
                await message.reply('Службы свыше запретили нам вмешиватся.')
            else:
                await message.reply('Мы раскрыли вашу истенную сущность.')
        if message.content in ['раскрой сущность всех']:
            if not(message.author.guild_permissions.administrator):
                await message.channel.send(self.gen_rand_word(2).title() + ', у вас нет доступа к этой комманде 😥')
                return
            if(message.guild == None):
                await message.reply('Данную команду можно использовать только на сервере!')
                return
            await message.reply('...')
            members = message.guild.members
            for i, member in enumerate(members):
                try:
                    await member.edit(nick=None)
                except:
                    await message.reply('Службы свыше запретили нам вмешиватся в судьбу ' + str(member.nick))
                else:
                    await message.reply('['+str(i)+'/'+str(len(members))+'] ' + str(member))
        if message.content in ['задай тему разговора', 'давай новую тему разговора']:
            lines = list(open('questions.txt', encoding="utf8"))
            question = random.choice(lines)
            await message.channel.send('Хорошо. Я задам такой вопрос:\n**' + question + '**\nПостарайтесь на него развёрнуто ответить и продолжить разговор вместе другими.\n' +
                                       'Если вы хотите поменять вопрос или разговор на прошлый исчерпан - напишите "давай новую тему разговора"')
        if original_layout_command.startswith('bf'):
            comm = original_layout_command.split(" ")
            if len(comm) == 2:
                await message.channel.send(bf.run(comm[1]))
        if original_layout_command.startswith('?chat'):
            mess = original_layout_command.split(" ")
            if len(mess) >= 2:
                await message.add_reaction('\N{THINKING FACE}')
                text = ' '.join(mess[1:])
                for i in range(1):
                    headers = {'User-Agent': UserAgent().random}
                    payload = {'inputs': text, 'key': 'XDGGECL86F7ABPLBG4OFQL2EBD5XR5NLIV4'}
                    text = requests.get('https://api.betterapi.net/youchat', params=payload, headers=headers).json()
                    if 'generated_text' in text:
                        break
                    time.sleep(1)

                if 'generated_text' in text:
                    gen_text = text['generated_text']
                    gen_text = gen_text.replace('&lt;', '<')
                    gen_text = gen_text.replace('&gt;', '>')
                    gen_text = gen_text.replace('&le;', '≤')
                    gen_text = gen_text.replace('&ge;', '≥')
                    gen_text = gen_text.replace('&amp;', '&')
                    gen_text = gen_text.replace('&nbsp;', ' ')
                    gen_text = gen_text.replace('&quot;', '"')
                    gen_text = gen_text.replace('&apos;', "'")
                    gen_text = gen_text.replace('&cent;', '¢')
                    gen_text = gen_text.replace('&pound;', '£')
                    gen_text = gen_text.replace('&yen;', '¥')
                    gen_text = gen_text.replace('&euro;', '€')
                    gen_text = gen_text.replace('&copy;', '©')
                    gen_text = gen_text.replace('&reg;', '®')
                    chunk_size = 1990  # Set the maximum size of each chunk
                    chunks = [gen_text[i:i+chunk_size] for i in range(0, len(gen_text), chunk_size)]
                    for chunk in chunks:
                        await message.channel.send(chunk)
                else:
                    if 'error' in text:
                        await message.channel.send(text['error'])
                    else:
                        await message.channel.send('Request error see the details in the console')
                        print(text)
                        print(headers, payload)
                #await message.remove_reaction('\N{THINKING FACE}')
                #await message.channel.send(text)
        if message.content in ['спс', 'спасибо', 'благодарю']:
            await message.add_reaction('\N{COOKIE}')


intents = discord.Intents.all()
intents.message_content = True
client = MyClient(intents=intents)
#client.run(conf.bot_token)
tree = app_commands.CommandTree(client)

@tree.command(name = "ping", description = "Ping the bot")
async def ping_command(interaction):
    await interaction.response.send_message("Pong!")

@tree.command(name = "whoami", description = "Who am i?")
async def whoami_command(interaction):
    await interaction.response.send_message("Ты - " + client.gen_rand_word(2) + ".")

@tree.command(name = "fact", description = "Get the fact")
async def fact_command(interaction):
    req = client.get_from('https://randstuff.ru/fact/generate/')
    if(req == False):
        res = 'Ошибка соединения с API: ' + client.req_error
    else:
        res = req['fact']['text']
    await interaction.response.send_message(res)

@tree.command(name = "whoisit", description = "Who is it?")
async def whoisit_command(interaction):
    await interaction.response.send_message("Я думаю, он  - " + client.gen_rand_word(2) + ".")

@tree.command(name = "google", description = "Search in google..")
async def google_command(interaction, search_msg:str):
    search_msg = '+'.join(search_msg.split())
    res_mess = f"Я думаю, это здась: [Google](https://www.google.com/search?q={search_msg})"
    await interaction.response.send_message(res_mess);
  
async def dl_worker(interaction, name: str, video: bool):
    start_dl = time.time()
    await interaction.response.send_message('[-1/3] Getting data...')
    tmp_dir = "tmp"
    r_filename = str(uuid.uuid4())
    ydl_opts = {
        'verbose': True,
        'format': 'bestaudio/best',
        'outtmpl': f"{tmp_dir}/{r_filename}.%(ext)s", # {tmp_dir}/%(title)s.%(ext)s
        'writethumbnail': True,
        'embedthumbnail': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }, {
            'key': 'FFmpegMetadata',
            'add_metadata': True,
        }, { # Embed thumbnail in file 
            'key': 'EmbedThumbnail', 
            'already_have_thumbnail': False, 
        }]
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if (name.startswith("http")):
                info = ydl.extract_info(f"{name}", download=False)
                url = info['webpage_url']
                d = int(info['duration'])
            else:
                # Search on ytMusic use ytmAPI
                ytm = ytmusicapi.YTMusic()
                info = ytm.search(name)[0]
                url = f"https://music.youtube.com/watch?v={info['videoId']}"
                d = int(info['duration_seconds'])
                # info = ydl.extract_info(f"ytsearch:{name}", download=False)['entries'][0] # Search in YouTube
            await interaction.edit_original_response(content='[1/3] Checking...')
            if d > 1000:
                raise Exception("Duration longest 1000s")
            title = info['title']
            ext = 'mp4' if video else 'mp3'
            r_filename = slugify(title)
            if (r_filename == None):
                r_filename = title.replace(' ', '-')
            file = f"{r_filename}.{ext}"
            path = os.getcwd() + '/' + (tmp_dir+'/'+file).strip()
            await interaction.edit_original_response(content=f"[2/3] Loading...")
            #ydl.download([url])
            # КостыльGaming inc (multi-threaded ultra asynchronous download)
            if (video):
                proc = await asyncio.create_subprocess_exec(
                    conf.yt_dlp_addr, '-f', 'b[filesize<=25M] / b[filesize_approx<=25M] / [tbr<600] / w',
                    '-S', 'res,ext:mp4:m4a', '--recode', ext,
                    '--ignore-errors', '--embed-thumbnail', '--progress', '--newline',
                    '--embed-metadata', '--output', f"{tmp_dir}/{r_filename}.%(ext)s", url,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE)
            else:
                proc = await asyncio.create_subprocess_exec(
                    conf.yt_dlp_addr, '-x', '--audio-format', 
                    'mp3', '--ignore-errors', '--embed-thumbnail', '--progress', '--newline',
                    '--embed-metadata', '--output', f"{tmp_dir}/{r_filename}.%(ext)s", url,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE)
            #stdout, stderr = await proc.communicate()
            #print(f'[{proc.returncode}]')
            #print(f'{stdout.decode()}')
            #print(f'{stderr.decode()}')
            start_dlg = time.time()-1
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                current_time = time.time()
                if current_time - start_dlg >= 1:
                    await interaction.edit_original_response(content='[2.5/3] '+line.decode().strip())
                    start_dlg = current_time
            await proc.wait()
            
            await interaction.edit_original_response(content='[3/3] Uploading...')

            check_file = os.path.exists(path)

            await interaction.edit_original_response(content=f"[4/3] Check file {str(check_file)} {file}...")
            
            if check_file:
                await interaction.edit_original_response(content=f"[5/3] Uploading...")
                time_dl = round(time.time() - start_dl, 2)
                title = f"{title} _({str(time_dl)}s)_"
                await interaction.edit_original_response(content=title,attachments=[discord.File(path)]);
                os.remove(path)

    except Exception as e:
        e = str(e)
        e = e.replace("\u001b\u005b\u0030\u003b\u0033\u0031\u006d", '**')
        e = e.replace("\u001b\u005b\u0030\u006d", '**')
        e = e.replace("\u001b\u005b\u0030\u003b\u0039\u0034\u006d", '**')
        await interaction.edit_original_response(content=e)


@tree.command(name = "dl", description = "download")
async def dl_command(interaction, name:str, video: bool=False):
    await dl_worker(interaction, name, video)
    


# Clear temp directory
for f in os.listdir('tmp'):
    os.remove(os.path.join('tmp', f))

client.run(conf.bot_token)
