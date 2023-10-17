import json
import random
from typing import Literal
from discord.ext import commands
from discord import app_commands, Embed, Colour, Member, Message, Interaction
from modules.utils import webhandler


class Chatbot(commands.Cog, name="Chatbot"):
    
    user_chatbot_uid = {}
    user_chatbot_type = {}
    users_disscussed_chatbot = []
    bots = {
        'Бот': 'main',
        'Кристина': 'kristina',
        'Незнакомка': 'чат-с-девушкой',
        'Обезьяна': 'тролль-бот-обезьяна',
        'Киса': 'чат-бот-киса',
        'Тролль': 'тролль-бот',
        'pBot': 'pbot',
        'Тян': 'Тян',
        'Иви': 'chat-bot-evie',
        'Неизвесный': 'бот-онлайн',
        'Бабка': 'old',
        'Владик': 'Владик',
        'Ваня': 'Ваня-Петух',
        'Спанч Бот': 'sponge-bot',
        'Добрый': 'Добрый',
        'Рудской': 'Рудской',
        'Леонид': 'Леонид',
        'Сапожник': 'сапожник',
        'Робобот': 'ROBOBOT',
        'Троечница': '3333',
        'Герой': 'hero',
        'Ява': 'java',
        'Патрик': 'patrick',
        'Татьяна': 'tatyana',
        'Лев': 'HappyLeo',
        'Геймер': 'gamer',
        'Крабик': 'Крабик',
        'Нармина': 'Нармина',
        'Строитель': 'строитель',
        'Соколов': 'Соколов',
        'Глупышка': 'silly',
        'Орк': 'ОРКИ',
        'Джинн': 'GiN'
    }
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='chatbot', description="Chat with a chat bot")
    async def chat_command(self, interaction: Interaction, action: Literal['start', 'stop']):
        if(action == 'start'):
            self.users_disscussed_chatbot.append(interaction.user)
            if interaction.user in self.user_chatbot_uid:
                del self.user_chatbot_uid[interaction.user]
            
            random_bot = random.choice(list(self.bots.keys()))
            self.user_chatbot_type.update({interaction.user:self.bots[random_bot]})
            # print(random_bot + " : " + self.bots[random_bot])
            await interaction.response.send_message("(Для остановки напиши одну из слкдующих фраз - **бот хватит**, **бот, хватит**, **бот, остановись** **остановить общение**)\n С вами общается **"+random_bot+"**")
            await interaction.followup.send("**"+random_bot+"**: Привет")
        elif(action == 'stop'):
            if interaction.user in self.users_disscussed_chatbot:
                self.users_disscussed_chatbot.remove(interaction.user)
            if interaction.user in self.user_chatbot_type:
                del self.user_chatbot_type[interaction.user]
                await interaction.response.send_message(random.choice(["Окей!", "Ладно!", "Пока!", "Прощай!", "До встречи!"]))
            else:
                await interaction.response.send_message("Dialog not started")
    
    @commands.Cog.listener("on_message")
    async def chatbot_messager(self, message: Message):
        raw_message = message.content
        if message.author in self.users_disscussed_chatbot:
            cbt = self.user_chatbot_type[message.author]
            bot_name_by_key = {v: k for k,v in self.bots.items()}
            if message.author in self.user_chatbot_uid:
                # print("  - UID : " + self.user_chatbot_uid[message.author])
                send_to_bot = self.post_form_chatbot(raw_message, self.user_chatbot_uid[message.author], self.user_chatbot_type[message.author])
            else:
                send_to_bot = self.post_form_chatbot(raw_message, '', cbt)
                self.user_chatbot_uid.update({message.author:send_to_bot['uid']})
            
            await message.reply("**"+ bot_name_by_key[cbt] + "**: " + str(send_to_bot['text']))

    @commands.command()
    async def uwu(self, ctx):
        await ctx.channel.send('uwu')

    def post_form_chatbot(self, text, uid='', bot=''):
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'}
        url = "https://xu.su/api/send"
        bot = "main" if '' else bot #main
        raw_data = {"bot":bot,"text":text}
        if uid != '':
            raw_data.update({"uid": uid}) 
        # print(raw_data)
        try:
            req = webhandler.post(url, data=raw_data, headers=headers, timeout=10)
        except:
            #return False
            return {
                    'ok': True,
                    'text': random.choice(['Я что-то думаю...', 'Я не могу ответить...', 'Мне не разрешили это говорить...', 'Вы ввели меня в ступор']),
                    'uid': uid
                   }
        else:
            return json.loads(req.text)


async def setup(bot):
    await bot.add_cog(Chatbot(bot))