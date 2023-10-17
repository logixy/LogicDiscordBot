import asyncio
import datetime
import random
import time
from typing import Literal
from discord.ext import commands
from discord import app_commands, Embed, Colour, Member
from lib.database import Database
from modules.Economics import Economy

class Minigames(commands.Cog, name="Minigames"):
    def __init__(self, bot):
        self.bot = bot
        self.economy = Economy()
        ldb = Database()
        self.db = ldb.db
        self.dbcur = ldb.cursor
        self.dbcur.execute("CREATE TABLE IF NOT EXISTS cave_game (id INTEGER PRIMARY KEY, time_start INTEGER, user_id VARCHAR(255), hunger INTEGER);")
        self.dbcur.execute("CREATE TABLE IF NOT EXISTS rewards (id INTEGER PRIMARY KEY, time INTEGER, user_id VARCHAR(255), reward VARCHAR(255));")

    @app_commands.command(name="banme")
    async def banme_command(self, interaction):
        await interaction.response.send_message("I don't want.")

    @app_commands.checks.cooldown(1, 3, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name = 'reward', description="Get your reward")
    async def reward_command(self, interaction, ephemeral: bool=True):
        # Daily reward period (sec)
        period = 60*60*12 # (12 hours)
        rewards = {'money': [300, 500, 800, 1000]}
        user_id = interaction.user.id
        data = self.db.execute("SELECT time FROM rewards WHERE time > ? AND user_id = ? ORDER BY time DESC LIMIT 1", [round(time.time())-period, user_id])
        last_reward_time = data.fetchone() # Last reward in period
        if last_reward_time is not None:
            delete_secs = last_reward_time[0]+period - time.time()
            await interaction.response.send_message(f"Вы уже получили награду. Следущую можете получить <t:{last_reward_time[0]+period}:R>", ephemeral=ephemeral, delete_after=delete_secs)
            return
        
        reward_time = round(time.time())
        money_count = random.choice(rewards['money'])
        self.economy.add_money(user_id, money_count)
        reward = f"Money **{money_count}$**"
        await interaction.response.send_message(f"Ваш приз ({reward})! Следующий <t:{round(time.time())+period}:R>", ephemeral=ephemeral)
        print("Give reward", interaction.user, reward)
        self.dbcur.execute("INSERT INTO rewards (time, user_id, reward) VALUES (?, ?, ?)", [reward_time, user_id, reward])
        self.db.commit()

    def render_game(self, gameMatrix) -> str:
        return ''.join(gameMatrix[0]) + \
        "\n" + ''.join(gameMatrix[1]) + \
        "\n" + ''.join(gameMatrix[2])
    
    @app_commands.checks.cooldown(1, 20, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name = "slots", description = "(100$) Play The Slots Game")
    async def slot_command(self, interaction, 
                        difficulty: Literal["easy", "normal", "hard", "AaAAAaA"] = "normal"):
        # Money logic
        if (self.economy.get_balance(interaction.user.id) < 100):
            await interaction.response.send_message("Недостаточно средств! (Необходимо **100$**)", delete_after=10)
            return
        self.economy.add_money(interaction.user.id, -100)
        
        # End money logic
        game_time = 20 # seconds
        slot_items = ['🍋', '🍒', '🍓', '🍇', '🍊', '🍉', '🍌', '🍍', '🥭', '🫐', '🌶', '🥕', '🥒', '🥑']
        slot_price = [ 50,    30,  25,   10,   8,    4,   10,   25,   25,   20,   90,   40,   60,  70 ]
        if (difficulty == "easy"):
            slot_items = slot_items[:2]
            prize_multiplier = 1
        if (difficulty == "normal"):
            slot_items = slot_items[:3]
            prize_multiplier = 2
        if (difficulty == "hard"):
            slot_items = slot_items[:5]
            prize_multiplier = 10
        if (difficulty == "AaAAAaA"):
            slot_items = slot_items
            prize_multiplier = 99
            
        game_matrix = [['🍋', '🍋', '🍋'],
                    ['🍋', '🍋', '🍋'],
                    ['🍋', '🍋', '🍋']]# Start pattern
        m1 = await interaction.response.send_message(self.render_game(game_matrix)) #, delete_after=game_time+15
        start_time = time.time()
        end_time = start_time+game_time
        speed_modifier = 0.3
        while True:
            if time.time() >= end_time:
                break
            game_progress = ((time.time() - start_time) / (game_time))*100
            # GENERATE NEW RANDOM LINE
            new_game_items = [random.choice(slot_items), random.choice(slot_items), random.choice(slot_items)]
            # MOVE LINE TO THE BOTTOM
            if game_progress < 40: # <40% of game we move all lines
                game_matrix = [new_game_items, game_matrix[0], game_matrix[1]]
            if (game_progress >= 40) and (game_progress < 70): # >40% of game progress we don't move wirst vertical line
                game_matrix = [[game_matrix[0][0],new_game_items[1],new_game_items[2]],
                            [game_matrix[1][0],game_matrix[0][1],game_matrix[0][2]],
                            [game_matrix[2][0],game_matrix[1][1],game_matrix[1][2]]]
            if game_progress >= 70: # 70% we don't move second vertical line
                game_matrix = [[game_matrix[0][0],game_matrix[0][1],new_game_items[2]],
                            [game_matrix[1][0],game_matrix[1][1],game_matrix[0][2]],
                            [game_matrix[2][0],game_matrix[2][1],game_matrix[1][2]]]

            await interaction.edit_original_response(content=self.render_game(game_matrix))
            await asyncio.sleep(2*speed_modifier)
            if game_progress < 100: speed_modifier = 0.5
            if game_progress < 70: speed_modifier = 0.4
            if game_progress < 40: speed_modifier = 0.3
        prize = 0
        prizelog = []
        prizelog.append("─"*35)
        for i in range(3):
            # Horizontal matches
            if game_matrix[i][0] == game_matrix[i][1] == game_matrix[i][2]:
                prize_price = slot_price[slot_items.index(game_matrix[i][0])] * 3
                prize += prize_price
                prizelog.append(f"│Horizontal match!    |{game_matrix[i][0]}|{str(prize_price).rjust(7)}$│")
            # Vertical matches
            if game_matrix[0][i] == game_matrix[1][i] == game_matrix[2][i]:
                prize_price = slot_price[slot_items.index(game_matrix[0][i])] * 2
                prize += prize_price
                prizelog.append(f"│Vertical match!      |{game_matrix[0][i]}|{str(prize_price).rjust(7)}$│")
        # Cross matches
        if game_matrix[0][0] == game_matrix[1][1] == game_matrix[2][2]:
            prize_price = slot_price[slot_items.index(game_matrix[1][1])] * 1
            prize += prize_price
            prizelog.append(f"│Cross match!         |{game_matrix[1][1]}|{str(prize_price).rjust(7)}$│")
        if game_matrix[0][2] == game_matrix[1][1] == game_matrix[2][0]:
            prize_price = slot_price[slot_items.index(game_matrix[1][1])] * 1
            prize += prize_price
            prizelog.append(f"│Cross match!         |{game_matrix[1][1]}|{str(prize_price).rjust(7)}$│")
        
        if prize == 0: 
            prizelog.append("|No matches           |   |       |")
        else:
            multiple_prize = prize * (prize_multiplier-1)
            prizelog.append(f"|Prize multipler      |{('x'+str(prize_multiplier)).rjust(3)}|{str(multiple_prize).rjust(7)}$│")
            prize += multiple_prize
        prizelog.append("─"*35)
        prizelog_text = '\n'.join(prizelog)
        await interaction.edit_original_response(content=f"{self.render_game(game_matrix)}\n───────\nВаш приз: **{prize}$**\n```{prizelog_text}\n```")
        self.economy.add_money(interaction.user.id, prize)
        
        if (prize<500):
            await asyncio.sleep(5)
            await interaction.delete_original_response()

    @app_commands.command(name = 'cave', description="Cave game (use /cave action:help)")
    async def cave_command(self, interaction, 
                            action: Literal["help", "start (50$)", "end", "status", "feed 🍎 (30$)", "feed 🍞 (60$)", "debug"],
                            target_user: Member = None,
                            ephemeral: bool=False):
        command_id = 1163557976636928101
        # Init used resources
        resources = {
            'pickaxe':     '<:stonepickaxe:1158872199529242704>',
            'cobblestone': '<:cobblestone:1158871916589883504>',
            'coal':        '<:coal:1158871907647639653>',
            'ironingot':   '<:iron:1158871909044338728>',
            'goldeningot': '<:goldeningot:1158871911745470544>',
            'diamond':     '<:diamond:1158871915096715356>',
            'apple':       '<:apple:1158872367553073182>',
            'bread':       '<:bread:1158872370157727905>',
        }
        
        title = f"{resources['pickaxe']} CaveGame {resources['pickaxe']}\n"
        message = ""
        
        ores = {
            'coal': {'cost': 0.2, 'weight': 0.3, 'min_weight': 0.1},
            'ironingot': {'cost': 2, 'weight': 0.2, 'min_weight': 0.1},
            'goldeningot': {'cost': 5, 'weight': 0.1, 'min_weight': 0.05},
            'diamond': {'cost': 15, 'weight': 0.05, 'min_weight': 0.005},
            'cobblestone': {'cost': 0.1, 'weight': 1, 'min_weight': 1} # All avilable
        }
        food_conf = {
            'feed 🍎 (30$)': {
                'price': 30,
                'feed': 2
            },
            'feed 🍞 (60$)': {
                'price': 60,
                'feed': 5
            }
        }
        max_hunger = 20
        user_id = interaction.user.id
        target_user_id = user_id
        if (target_user is not None): target_user_id = target_user.id 
        
        hunger_time = 60*60 # 1 hunger = 1 hour (in secs)
        resource_time = 60
        
        # Help
        help_food_list = ""
        help_items_list = ""
        max_avg_cost = 0
        min_avg_cost = 0
        for i, s in food_conf.items():
            help_food_list += f"\n</cave:{command_id}>`action:{i}` - восстановит **{s['feed']}** ед. голода."
        for i, s in ores.items():
            help_items_list += f"\n{resources[i]} - мв: **{s['min_weight']}**, Мв: **{s['weight']}**, цена за шт.: **{s['cost']}$**"
            if (s['weight'] == 1 or s['min_weight'] == 1):
                weight = 1 - max_avg_cost
                min_weight = 1 - min_avg_cost
            else:
                weight = s['weight']
                min_weight = s['min_weight']
            max_avg_cost += s['cost'] * weight
            min_avg_cost += s['cost'] * min_weight
        help_text = f'''Это небольшая игра, где вы отправляете шахтёра добывать ресурсы. 
    Учитывайте то, что у шахтёра есть статус голода. Если он дойдёт до нуля - все добытые ресурсы будут утеряны.
    ## Управление {resources['pickaxe']}
    Для начала игры используйте </cave:{command_id}>`action:start (50$)`
    Покормить шахтёра </cave:{command_id}>`action:food <тип_пищи>`
    Узнать статус добычи </cave:{command_id}>`action:status`
    Для завершения игры используйте </cave:{command_id}>`action:end`
    Отладочная информация </cave:{command_id}>`action:debug`
    ## Механика голода {resources['apple']}
    Изначально у шахтёра **{max_hunger}** очков голода.
    Голод тратится линейно **1** ед в **{hunger_time}** сек.
    Вы можете покормить шахтёра, для этого используйте:{help_food_list}
    ## Руды {resources['diamond']}
    Скорость добычи: **1** предмет в **{resource_time}** сек.
    С завершением идёт общий подсчёт добытых предметов.
    Вероятности их встречи от минимального [мв] до максимального  [Мв]
    Текущий список возможных предметов:{help_items_list}
    Прогноз дохода за один предмет: **{min_avg_cost}$** мин. **{max_avg_cost}$** макс.
    ## Взаимодействие с другими игроками 🍞
    Узнать статус игры другого игрока </cave:{command_id}>`action:status target_user:@пользователь`
    Покормить шахтёра другого игрока </cave:{command_id}>`action:food <тип_пищи> target_user:@пользователь`
        '''
        
        # Getting active cave session if exists
        data = self.db.execute("SELECT * FROM cave_game WHERE user_id=?", [target_user_id])
        cave_session = data.fetchone()
        
        if cave_session is not None:
            mine_time = round(time.time() - cave_session[1])
            hunger = round(cave_session[3] - mine_time/hunger_time)
            mined = round(mine_time/resource_time) 
            # Check if death
            if (hunger <= 0):
                death_time = cave_session[1] + cave_session[3]*hunger_time
                message = f"## **💀 Умер от голода:** (<t:{death_time}:R>)"
                self.db.execute("DELETE FROM cave_game WHERE id = ?", [cave_session[0]])
                self.db.commit()
        
        while True:
            if message:
                break
                
            if (action == "debug"):
                res_test = "**Loaded resources**: "
                for key, value in resources.items():
                    res_test += value
                    
                sess_test = "**Cave session:** " + str(cave_session)
                message = res_test+"\n"+sess_test
                break
            if (action == "help"):
                message = help_text
            if (action == "start (50$)"):
                if (user_id != target_user_id):
                    message = "Вы не можете запускать игру другого игрока!"
                if cave_session is not None:
                    message = "Процесс добычи уже был запущен!"
                if (self.economy.get_balance(user_id) < 50):
                    message = "Недостаточно средств!"
                
                self.economy.add_money(user_id, 50*-1)
                self.db.execute("INSERT INTO cave_game (time_start, user_id, hunger) VALUES (?, ?, ?)", [round(time.time()), user_id, max_hunger])
                self.db.commit()
                message = f"## :arrow_forward:Начало добычи\nНе забывайте проверять статус процесса добычи </cave:{command_id}>` action:status`"
                break
            if (action == "status"):
                if (user_id != target_user_id):
                    title_status = f"**Статус добычи {target_user.display_name}**\n\n"
                else:
                    title_status = f"**Статус добычи** \n\n"
                if cave_session is None:
                    message = f"{title_status}\n**Процесс добычи не запущен!**"
                    
                if not message:
                    message = title_status \
                            + f"⌛**В шахте уже:** **{mine_time}** сек\n" \
                            + f"🍴**Голод:** **{hunger}**\n" \
                            + f"📊**Добыто ресурсов:** **{mined}**\n" \
                            + f"📈**Максимальный прогноз доходности:** **{round(mined*max_avg_cost, 2)}$**\n" \
                            + f"📉**Минимальный прогноз доходности:** **{round(mined*min_avg_cost, 2)}$**\n"
            if (action in ["feed 🍎 (30$)", "feed 🍞 (60$)"]):
                if cave_session is None:
                    message = "**Процесс добычи не запущен!**"
                    break
                if (hunger >= max_hunger):
                    message = "Шахтёр отказывается от пищи, так как не голоден."
                    break            
                if (self.economy.get_balance(user_id) < food_conf[action]['price']):
                    message = "Недостаточно средств ({action})"
                    break
                
                self.economy.add_money(user_id, food_conf[action]['price']*-1)
                if (hunger + food_conf[action]['feed'] > max_hunger):
                    add_hunger = food_conf[action]['feed'] - (hunger + food_conf[action]['feed'] - max_hunger)
                else:
                    add_hunger = food_conf[action]['feed']
                    
                self.db.execute("UPDATE cave_game SET hunger=hunger+? WHERE id=?", [add_hunger, cave_session[0]])
                self.db.commit()
                ti = f"**{resources['apple']} Вы накормили шахтёра**\n---------\n"
                if (user_id != target_user_id):
                    ti = f"**{resources['apple']} Вы накормили шахтёра {target_user.display_name}**\n---------\n"
                message = f"{ti}**Использовано: {action.title()}**!\n**Статус голода: {hunger+add_hunger}**"
            if (action == "end"):
                if (user_id != target_user_id):
                    message = "Вы не можете останавливать игру другого игрока!"
                    break
                if cave_session is None:
                    message= "**Процесс добычи не запущен!**"
                    break
                result = f"**Завершение процесса добычи (Добыто: {mined})** {resources['pickaxe']}\n---------\n"
                result_cost = 0
                for ore, params in ores.items():
                    if ((params['weight'] >= 1) or (params['min_weight'] >= 1)):
                        ore_count = mined # if weight 1 - use all mined items
                    else:
                        ore_count = round(mined * random.uniform(params['min_weight'], params['weight']))
                    mined = mined - ore_count
                    cost = round(ore_count * params['cost'], 2)
                    result_cost += cost
                    result += f"{resources[ore]}x**{ore_count}**({params['cost']}$) (**{cost}$**)\n"
                result_cost = round(result_cost, 2)
                result += f"**{'-' * 26}**\n### **{str(result_cost).rjust(40)}$**"
                
                # Give money to user
                self.economy.add_money(user_id, result_cost)
                # Delete session (end game)
                self.db.execute("DELETE FROM cave_game WHERE id = ?", [cave_session[0]])
                self.db.commit()
                
                message = result
                break
        
        embed = Embed(
            title=title,
            description=message,
            colour=Colour.green(),
            timestamp=datetime.datetime.now())
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        if (target_user is not None):
            embed.set_thumbnail(url=target_user.display_avatar.url)
        #await interaction.response.send_message(title+message, ephemeral=ephemeral)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    @app_commands.command(name = "guess", description = "Guess the number.")
    async def guess_command(self, interaction, max: int = 10):
        # Генерация случайного числа от 1 до {max}
        if max > 0:
            number = random.randint(1, max)
        else:
            number = random.randint(max, 1)
        
        await interaction.response.send_message(f"Угадай число от 1 до {str(max)}!")

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        guess = await self.bot.wait_for('message', check=check)

        try:
            # Преобразование введенного значения в целое число
            user_guess = int(guess.content)
        except ValueError:
            await interaction.channel.send('Некорректный ввод! Введите число.', delete_after=5)
            return

        if user_guess == number:
            await interaction.channel.send('Поздравляю, вы угадали число!', delete_after=5)
        else:
            await interaction.channel.send(f'Неправильно! Число было {number}.', delete_after=5)
        await asyncio.sleep(5)
        await guess.delete()
        await interaction.delete_original_response()


async def setup(bot):
    await bot.add_cog(Minigames(bot))