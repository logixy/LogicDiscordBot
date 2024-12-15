import asyncio
import random
from collections import Counter
from urllib.parse import urlparse
from discord.ext import commands
from discord import app_commands, Embed, Colour, Interaction, Message
from modules.utils import webhandler


class Randstuff(commands.Cog, name="Randstuff"):
    def __init__(self, bot):
        self.bot = bot
        self.embed = Embed(
          title="RandStuff",
          description="content",
          colour=Colour.gold())

    @app_commands.command(name="joke", description="Generate random joke")
    async def joke_command(self, interraction: Interaction):
        self.embed.title = "Анекдот"
        self.embed.description = self.get_joke()
        await interraction.response.send_message(embed=self.embed)

    @app_commands.command(name="fact", description="Generate random fact")
    async def fact_command(self, interraction: Interaction):
        self.embed.title = "Факт"
        self.embed.description = self.get_fact()
        await interraction.response.send_message(embed=self.embed)
    
    @app_commands.command(name="where", description="Where?")
    async def where_command(self, interraction: Interaction):
        await interraction.response.send_message(self.get_where())

    @app_commands.command(name = "whoami", description = "Who am i?")
    async def whoami_command(self, interaction: Interaction):
        await interaction.response.send_message(f"Ты - {self.gen_rand_word(2)}.")

    @app_commands.command(name = "whoisit", description = "Who is it?")
    async def whoisit_command(self, interaction: Interaction):
        await interaction.response.send_message(f"Я думаю, он  - {self.gen_rand_word(2)}.")

    @app_commands.command(name="randnick", description="Generates a random nick for you")
    async def randnick_command(self, interaction: Interaction):
        self.embed.title = "Паспортный стол (наверное)"
        self.embed.description = random.choice(["Придумываем...",
           "Вычисляем вычисления...", "Спрашиваем мимопроходящих...",
           "Завём тётю Галю...", "Делаем серьёзный вид..."])
        await interaction.response.send_message(embed=self.embed)
        asyncio.sleep(3)
        newNick = self.get_rand_nickname()
        try:
            await interaction.user.edit(nick=newNick)
        except:
            msg = 'Мы подобрали Вам новое имя: **' + newNick + '**\n' + \
                'Но, службы свыше запретили нам вмешиваться. Так что сменить данные вы можете вручную.'
        else:
            msg = 'Добро пожаловать, **' + newNick + '**, которого мы никогда не видели :face_with_hand_over_mouth:\n'
        self.embed.description = msg
        await interaction.edit_original_response(embed=self.embed)
    
    @app_commands.command(name = "google", description = "Search in google.")
    async def google_command(self, interaction, search_msg:str):
        search_msg = '+'.join(search_msg.split())
        res_mess = f"Я думаю, это здась: [Google](https://www.google.com/search?q={search_msg})"
        await interaction.response.send_message(res_mess)

    @app_commands.command(name = "surl", description = "Short the link")
    async def surl_command(self, interaction: Interaction, link:str):
        embed = Embed(color=Colour.orange(), title="🔗 URL shorter")
        if self.is_url(link) is False:
            embed.description = "Link is not valid url"
            await interaction.response.send_message(embed=embed)
            return
        
        embed.description = "Shorted link: {}".format(self.short_url(link))
        await interaction.response.send_message(embed=embed)

    
    def short_url(self, url):
        base_url = 'http://tinyurl.com/api-create.php'
        data = {'url': url}
        response = webhandler.post(base_url, data=data)
        short_url = response.text
        return short_url
    
    def is_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def get_joke(self) -> str:
        data = webhandler.get_json('https://randstuff.ru/joke/generate/')
        if('joke' not in data):
            return 'API Error: ' + webhandler.req_error
        else:
            return data['joke']['text']

    def get_fact(self) -> str:
        data = webhandler.get_json('https://randstuff.ru/fact/generate/')
        if('fact' not in data):
            return 'API Error: ' + webhandler.req_error
        else:
            return data['fact']['text']

    def get_where(self) -> str:
        data = webhandler.get_json('https://randstuff.ru/city/generate/')
        if('city' not in data):
            return 'API Error: ' + webhandler.req_error
        else:
            return f"Я думаю, в городе {data['city']['city']} ({data['city']['country']})."
    
    def get_rand_question(self) -> str:
        lines = list(open('modules/randstuff/questions.txt', encoding="utf8"))
        return random.choice(lines)
    
    def get_rand_nickname(self) -> str:
        if random.choice([True, False]):
            return self.gen_rand_word(2).title() + " " + \
                self.gen_rand_word(1).title()
        else:
            randNicks = webhandler.post_json('https://plarium.com/services/api/nicknames/new/create?group=2&gender=2')
            return random.choice(randNicks)
        
    def gen_rand_word(self, type):  # type 2 - adjective (прилагать.) 1 - noun (сущ.)
        if(type == 2):
            lines = list(open('modules/randstuff/adjectives.txt', encoding="utf8"))
        else:
            lines = list(open('modules/randstuff/nouns.txt', encoding="utf8"))
        return random.choice(lines).strip()

    @commands.Cog.listener("on_message")
    async def chat_message(self, message: Message):
        if message.author.bot or not message.content:
            return

        message_text = message.content
        lowered_message = message_text.lower()
        mc_e = Counter(lowered_message).most_common(1)[0] # most common element

        if len(message_text)/100*50 < mc_e[1] and len(message_text) > 3:
            sta = mc_e[0] * random.randint(10, 30)
            await message.reply(self.upper_case_random_chars(sta))

        if lowered_message in ['бип', 'боп', 'буп']:
            await message.reply(random.choice(['Бип', 'Боп', 'Буп', 'null', 'undefined', 'out of bounds', 'себе по'+lowered_message+'ай', \
            'Я в своем познании настолько преисполнился что я как будто бы уже сто триллионов миллиардов лет проживаю на триллионах и триллионах таких же планет, понимаешь как эта земля.']))

        if lowered_message in ['делать?', 'строить?', 'b8', 'получится?', 'получилось?', 'вышло?', 'выйдет?']:
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
            await message.reply(random.choice(answ8) + " " + random.choice(emojies))

        if lowered_message in ['спс', 'спасибо', 'благодарю']:
            await message.add_reaction('\N{COOKIE}')

        if lowered_message in ['шуткани', 'пошути', 'анекдот']:
            await message.channel.send(self.get_joke())
        
        if lowered_message in ['факт', 'истина']:
            await message.channel.send(self.get_fact())

        if lowered_message in ['где?', 'где он?', 'где она?', 'где я?', 'где я оказался?', 'где же я?', 'где я нахожусь?', 'где я сейчас?', 'где я сейчас нахожусь?']:
            await message.channel.send(self.get_where())

        if lowered_message in ['ктоя?', 'кто я?', 'кто я есть?', 'кто же я?', 'ну кто же я?', 'божечки, что я такое?!', 'хто я?']:
            await message.reply("Ты - " + self.gen_rand_word(1) + ".")
        
        if lowered_message in ['кто?', 'кто она?', 'хто она?', 'кто ты?', 'кто он?', 'кто же он?', 'кто же ты?', 'хто он?', 'хто же он?', 'хто ты?']:
            await message.reply("Я думаю, он - " + self.gen_rand_word(1) + ".")
        
        if lowered_message in ['почему я?', 'почему он?', 'почему они?', 'почему мы?', 'почему она?', 'почему?']:
            await message.reply("Потому что " + self.gen_rand_word(1) + ".")

        if lowered_message in ['задай тему разговора', 'давай новую тему разговора']:
            await message.reply('Хорошо. Я задам такой вопрос:\n**' + self.get_rand_question() + '**\nПостарайтесь на него развёрнуто ответить и продолжить разговор вместе другими.\n' +
                                       'Если вы хотите поменять вопрос или разговор на прошлый исчерпан - напишите "давай новую тему разговора"') 

        if lowered_message in ['сменимненик', 'смени мне никнейм', 'смени мне ник', 'смени мой ник', 'измени мой ник']:
            if(message.guild is None):
                await message.channel.send('Данную команду можно использовать только на сервере!')
                return
            await message.channel.send('Печатаем новый паспорт...')
            newNick = self.get_rand_nickname()
            try:
                await message.author.edit(nick=newNick)
            except:
                msg = 'Мы подобрали Вам новое имя: **' + newNick + '**\n' + \
                    'Но, службы свыше запретили нам вмешиваться. Так что сменить данные вы можете вручную.'
                await message.reply(msg)
            else:
                msg = 'Добро пожаловать, **' + newNick + '**, которого мы никогда не видели :face_with_hand_over_mouth:\n'
                await message.channel.send(msg)      
    
    def upper_case_random_chars(self, string):
        result = ""
        for char in string:
            if random.choice([True, False]):
                result += char.upper()
            else:
                result += char
        return result


async def setup(bot):
    await bot.add_cog(Randstuff(bot))
