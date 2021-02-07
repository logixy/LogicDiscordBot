import discord, requests, json
from discord.ext import tasks, commands
import config as conf
from ProjectEverydayLogo import MakePerfect as mpi
		
class MyClient(discord.Client):
	async def on_ready(self):
		print('Logged on as', self.user)
		print('Uid:',self.user.id)
		
	def get_from(self, url):
		headers = {'X-Requested-With': 'XMLHttpRequest', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'}
		return json.loads(requests.get(url, headers=headers).text)
	
	async def on_message(self, message):
        # don't respond to ourselves
		if message.author == self.user:
			return

		message.content = message.content.lower()
		#print(message.content)
		if(message.content == '<@!'+str(self.user.id)+'>'):
			text = 'Что Вам необходимо?\n ' + \
			'**Доступные команды на данный момент:** \n' + \
			'`Cмени аву плз` - Смена аватара сервера на случайно сгенерированный\n' + \
			'`Бип` - Послать ботов\n' + \
			'`Шуткани` -  Случайная шутка\n' + \
			'`Факт` - Случайный факт\n' + \
			'`Топ голосующих` - Вывести топ голосующих на текущий момент\n' + \
			'`Статус серверов` - Узнать статус игровых серверов\n'
			await message.channel.send(text)
			
		if message.content == 'бип':
			await message.channel.send('Буп')
				
		if message.content == 'смени аву плз':
			if(message.guild == None):
				await message.channel.send('Данную команду можно использовать только на сервере!')
				return;
			await message.channel.send('Окей..')
			mpi.generateIcon()
			server = discord.Client.get_guild(self, id=message.guild.id)
			
			with open('ProjectEverydayLogo/out/out.png', 'rb') as f:
				icon = f.read()
			await server.edit(icon=icon)
			await message.channel.send('Нати.')
		if message.content == 'шуткани':	
			await message.channel.send(self.get_from('https://randstuff.ru/joke/generate/')['joke']['text'])
		if message.content == 'факт':
			await message.channel.send(self.get_from('https://randstuff.ru/fact/generate/')['fact']['text'])
		if message.content == 'топ голосующих':
			positions = ['Первое место', 'Второе место', 'Третье место', 'Четвёртое место', 'Пятое место']
			spisok = self.get_from('https://logicworld.ru/launcher/tableTopVote.php?mode=api')
			text = "На текущий момент топ голосующих такой:\n"
			i = 0
			for userdata in spisok:
				static_text = " - **" + userdata['user'].title() + "** Счёт - **" + userdata['ammount'] + "** Доп. голоса - **" + userdata['cheatAmmount'] + "**\n"
				if i < len(positions):
					text += positions[i] + static_text
				else:
					text += str(i+1) + static_text
				i += 1
			await message.channel.send(text)
		if message.content == 'статус серверов':
			spisok = self.get_from('https://logicworld.ru/monAJAX/ajax.php')
			text = "Статус игровых серверов:\n"
			for s_name in spisok['servers']:
				s_data = spisok['servers'][s_name]
				if ( s_data['status'] == 'online' ):
					text += "**"+ s_name +"** - ("+ str(s_data['online']) + "/" + str(s_data['slots']) + ")" + "\n"
				else:
					text += "**"+s_name+"** - (**"+ s_data['status'].title() + "**)" + "\n"
			await message.channel.send(text)

client = MyClient()
client.run(conf.bot_token)
