import discord, requests, json, random
from requests.exceptions import Timeout
from discord.ext import tasks, commands
import config as conf
from ProjectEverydayLogo import MakePerfect as mpi
		
class MyClient(discord.Client):
	req_error = ''
	async def on_ready(self):
		print('Logged on as', self.user)
		print('Uid:',self.user.id)
		
	def get_from(self, url):
		headers = {'X-Requested-With': 'XMLHttpRequest', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'}
		try:
			req = requests.get(url, headers=headers, timeout=8)
		except Timeout:
			self.req_error = 'Превышено время ожидания :cold_face:'
			return False
		else:
			return json.loads(req.text)
	
	def gen_rand_word(self, type): #type 2 - adjective (прилагать.) 1 - noun (сущ.)
		req = self.get_from('http://free-generator.ru/generator.php?action=word&type='+str(type))
		if(req == False):
			message.channel.send('Ошибка соединения с API: '+self.req_error)
			return
		
		return req['word']['word']
	
	async def on_message(self, message):
        # don't respond to ourselves
		if message.author == self.user:
			return

		message.content = message.content.lower()
		#print(message.content)
		if(message.content == '<@!'+str(self.user.id)+'>'):
			text = 'Что Вам необходимо?\n ' + \
			'**Доступные команды на данный момент:** \n' + \
			'<@!'+str(self.user.id)+'> - Вызвать данную подсказку\n' + \
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
			
		if message.content in ['бип', 'боп', 'буп']:
			await message.reply(random.choice(['Бип', 'Боп', 'Буп']))
				
		if message.content in ['смени аву плз', 'смени аватар сервера', 'смени иконку сервера', 'смени иконку плз']:
			if(message.guild == None):
				await message.channel.send('Данную команду можно использовать только на сервере!')
				return;
			m2 = ['Передаю вашу заявку нашему художнику...', 'Снижаем ЗП дизайнера...', 'Вызываем омон в дом художника...',\
			'Вежливо уговариваем художника...', 'Под пытками заставляем нашего дизайнера...']
			await message.reply('Принято! ' + random.choice(m2))
			mpi.generateIcon()
			server = discord.Client.get_guild(self, id=message.guild.id)
			
			with open('ProjectEverydayLogo/out/out.png', 'rb') as f:
				icon = f.read()
			await server.edit(icon=icon)
			await message.reply('Готово!')
		if message.content in ['шуткани', 'пошути', 'анекдот']:
			req = self.get_from('https://randstuff.ru/joke/generate/')
			if(req == False):
				await message.reply('Ошибка соединения с API: '+self.req_error)
				return
			await message.channel.send(req['joke']['text'])
		if message.content in ['факт', 'истина']:
			req = self.get_from('https://randstuff.ru/fact/generate/')
			if(req == False):
				await message.reply('Ошибка соединения с API: '+self.req_error)
				return
			await message.channel.send(req['fact']['text'])
		if message.content in ['топ голосующих', 'топ голосов', 'топ голосовавших']:
			spisok = self.get_from('https://logicworld.ru/launcher/tableTopVote.php?mode=api')
			if(spisok == False):
				await message.reply('Ошибка соединения с API: '+self.req_error)
				return
			text = "На текущий момент топ голосующих такой:\n"
			i = 0
			for userdata in spisok:
				static_text = " - **" + userdata['user'].replace('_', '\\_').title() + "** Счёт - **" + userdata['ammount'] + "** Доп. голоса - **" + userdata['cheatAmmount'] + "**\n"
				text += str(i+1) + static_text
				i += 1
			await message.reply(text)
		if message.content in ['статус серверов', 'статус сервера', 'server stat', 'статистика сервера']:
			spisok = self.get_from('https://logicworld.ru/monAJAX/ajax.php')
			if(spisok == False):
				await message.reply('Ошибка соединения с API: '+self.req_error)
				return
			text = "Статус игровых серверов:\n"
			for s_name in spisok['servers']:
				s_data = spisok['servers'][s_name]
					
				if ( s_data['status'] == 'online' ):
					stat_e = ':green_circle:'
					if (s_data['ping'] > 300):
						stat_e = ':yellow_circle:'
					if (s_data['ping'] > 350):
						stat_e = ':orange_circle:'
					if (s_data['ping'] > 450):
						stat_e = ':brown_circle:'
					text += stat_e+"**"+ s_name +"** - ("+ str(s_data['online']) + "/" + str(s_data['slots']) + ") (" + str(s_data['ping']) + "ms)\n"
				else:
					text += ":red_circle:**"+s_name+"** - (**"+ s_data['status'] + "**)" + "\n"
			text += "\n**Общий онлайн:** " + str(spisok['online']) + "/" + str(spisok['slots']) + "\n"
			text += "**Рекорд дня:** " + str(spisok['recordday']) + " (" + spisok['timerecday'] + ")\n"
			text += "**Рекорд:** " + str(spisok['record']) + " (" + spisok['timerec'] + ")\n"
			await message.reply(text)
		if message.content in ['кто я?', 'кто я есть?', 'кто же я?', 'ну кто же я?', 'божечки, что я такое?!']:			
			await message.reply("Ты " + self.gen_rand_word(2) + ".")
		if message.content in ['кто ты?', 'кто он?', 'кто же он?', 'кто же ты?']:			
			await message.reply("Я думаю он " + self.gen_rand_word(2) + ".")
		if message.content in ['где я?', 'где я оказался?', 'где же я?', 'где я нахожусь?', 'где я сейчас?', 'где я сейчас нахожусь?']:			
			req = self.get_from('https://randstuff.ru/city/generate/')
			await message.reply("Ты в городе " + req['city']['city'] + " ("+req['city']['country']+").")
		if message.content in ['получится?', 'получилось?', 'вышло?', 'выйдет?']:
			answ8 = ['Бесспорно', 'Предрешено', 'Никаких сомнений', 'Определённо да',\
			'Можешь быть уверен в этом', 'Мне кажется — «да»', 'Вероятнее всего',\
			'Хорошие перспективы', 'Знаки говорят — «да»', 'Да',\
			'Пока не ясно, попробуй снова', 'Спроси позже', 'Лучше не рассказывать',\
			'Сейчас нельзя предсказать', 'Сконцентрируйся и спроси опять',\
			'Даже не думай', 'Мой ответ — «нет»', 'По моим данным — «нет»',\
			'Перспективы не очень хорошие', 'Весьма сомнительно']
			emojies = [':smiling_face_with_3_hearts:', ':sweat_smile:', ':sunglasses:',\
			':upside_down:', ':point_up:', ':thinking:', ':woman_shrugging:', ':face_with_raised_eyebrow:',\
			':eyes:', ':woman_gesturing_no:', ':dancer:', ':no_mouth:']
			await message.reply(random.choice(answ8).lower() + " " + random.choice(emojies))
		if message.content in ['пинг', 'ping', 'пинг!', 'ping!']:
			await message.reply('Понг!')
		if message.content in ['смени мне никнейм', 'смени мне ник', 'смени мой ник', 'измени мой ник']:
			if(message.guild == None):
				await message.channel.send('Данную команду можно использовать только на сервере!')
				return;
			await message.channel.send('Печатаем новый паспорт...')
			req = self.get_from('http://free-generator.ru/generator.php?action=word&type=2')
			if(req == False):
				await message.reply('Ошибка соединения с API: '+self.req_error)
				return
			req2 = self.get_from('http://free-generator.ru/generator.php?action=word&type=1')
			if(req2 == False):
				await message.reply('Ошибка соединения с API: '+self.req_error)
				return
			newNick = req['word']['word'].title() + " " + req2['word']['word'].title();
			try:
				await message.author.edit(nick=newNick)
			except:
				await message.reply('Службы свыше запретили нам вмешиватся.')
			else:
				profession = json.loads(requests.post('https://randomall.ru/api/general/jobs').text)
				msg = 'Добро пожаловать, **' + newNick + '**, которого мы никогда не видели :face_with_hand_over_mouth:\n' + \
				'Вы '+profession
				await message.channel.send(msg)
		if message.content in ['сбрось мой ник', 'сбрось мне ник', 'скинь мой ник']:
			if(message.guild == None):
				await message.reply('Данную команду можно использовать только на сервере!')
				return;
			try:
				await message.author.edit(nick=None)
			except:
				await message.reply('Службы свыше запретили нам вмешиватся.')
			else:
				await message.reply('Мы раскрыли вашу истенную сущность.')
		if message.content in ['задай тему разговора', 'давай новую тему разговора']:
			lines = list(open('questions.txt', encoding="utf8"))
			question =random.choice(lines)
			await message.channel.send('Хорошо. Я задам такой вопрос:\n**'+question+'**\nПостарайтесь на него развёрнуто ответить и продолжить разговор вместе другими.\n' + \
			'Если вы хотите поменять вопрос или разговор на прошлый исчерпан - напишите "давай новую тему разговора"')

client = MyClient()
client.run(conf.bot_token)
