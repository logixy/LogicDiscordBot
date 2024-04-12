import asyncio
import datetime
import random
import time
from typing import Literal
from discord.ext import commands
from discord import app_commands, Embed, Colour, Member
from lib.database import Database
from modules.Economics import Economy

# ConnectFour logic START
# Source: https://github.com/jaketanda/jankebot/blob/main/cogs/connectfour.py
async def confirmation(self, message, sentUser, channel, successMessage = ':white_check_mark: Operation successful', cancelledMessage = ':x: Operation cancelled'):
    new_message = await channel.send(message)

    await new_message.add_reaction('✅')
    await new_message.add_reaction('❌')

    def check(reaction, user):
        return user == sentUser

    reaction = None

    while True:
        if str(reaction) == '✅':
            await new_message.clear_reactions()
            await new_message.edit(content=successMessage)
            return True
        elif str(reaction) == '❌':
            await new_message.clear_reactions()
            await new_message.edit(content=cancelledMessage)
            return False

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout = 30.0, check = check)
            await new_message.remove_reaction(reaction, user)
        except:
            await new_message.clear_reactions()
            await new_message.edit(content=cancelledMessage)
            return False

def getColorSelection(x):
    if x == 1:
        return 'red'
    elif x == 2:
        return 'yellow'
    else:
        return 'black'

def getColorGrid(x):
    if x == 1:
        return 'red'
    elif x == 2:
        return 'yellow'
    elif x == 0:
        return 'white'
    else:
        return 'blue'

def moveSelection(selection, playerNum, spotsToMove):
    for index, item in enumerate(selection):
        if item != 0:
            selection[index] = 0
            newPos = index + spotsToMove
            if newPos < 0:
                newPos = 0
            elif newPos > 6:
                newPos = 6
            selection[newPos] = playerNum
            break
    return selection

def isPlacementPossible(selection, grid):
    for pos, item in enumerate(selection):
        if item != 0:
            break

    height = 5
    while True:
        if height < 0:
            break
        if grid[height][pos] == 0:
            return True
        height -= 1
    return False

def updateGrid(selection, grid):
    symbol = 0
    for pos, item in enumerate(selection):
        if item != 0:
            symbol = item
            break

    height = 5
    while True:
        if height < 0:
            break
        if grid[height][pos] == 0:
            grid[height][pos] = symbol
            break
        height -= 1
    return grid

def changeSelectionColor(selection):
    for index, item in enumerate(selection):
        if item == 1:
            selection[index] = 0
            selection[3] = 2
            break
        elif item == 2:
            selection[index] = 0
            selection[3] = 1
            break
    return selection

def checkForWinner(selection, grid):
    foundWinner = False
    symbol = 0
    for pos, item in enumerate(selection):
        if item != 0:
            symbol = item
            break

    height = 5
    for x in range(5):
        if grid[x][pos] == symbol and (x == 0 or grid[x-1][pos] == 0):
            height = x
            break
        
    #check horizontal
    inarow = 0
    for x in range(7):
        if grid[height][x] == symbol:
            inarow += 1
            if inarow >= 4:
                grid[height][x] = 3
                grid[height][x-1] = 3
                grid[height][x-2] = 3
                grid[height][x-3] = 3
                foundWinner = True
        else:
            inarow = 0

    #check vertical
    inarow = 0
    for x in range(6):
        if grid[x][pos] == symbol or grid[x][pos] == 3:
            inarow += 1
            if inarow >= 4:
                grid[x][pos] = 3
                grid[x-1][pos] = 3
                grid[x-2][pos] = 3
                grid[x-3][pos] = 3
                foundWinner = True
        else:
            inarow = 0  

    #check diagonal negative slope
    inarow = 0
    for x in range(-5, 6):
        if height+x >= 0 and height+x <= 5 and pos+x >= 0 and pos+x <= 6 and (grid[height+x][pos+x] == symbol or grid[height+x][pos+x] == 3):
            inarow += 1
            if inarow >= 4:
                grid[height+x][pos+x] = 3
                grid[height+x-1][pos+x-1] = 3
                grid[height+x-2][pos+x-2] = 3
                grid[height+x-3][pos+x-3] = 3
                foundWinner = True
        else:
            inarow = 0  

    #check diagonal positive slope
    inarow = 0
    for x in range(-5, 6):
        if height-x >= 0 and height-x <= 5 and pos+x >= 0 and pos+x <= 6 and (grid[height-x][pos+x] == symbol or grid[height-x][pos+x] == 3):
            inarow += 1
            if inarow >= 4:
                grid[height-x][pos+x] = 3
                grid[height-x+1][pos+x-1] = 3
                grid[height-x+2][pos+x-2] = 3
                grid[height-x+3][pos+x-3] = 3
                foundWinner = True
        else:
            inarow = 0
        
    if foundWinner:
        return symbol

    #check if grid is full (tie scenario)
    gridNotFull = False
    for x in grid:
        for y in x:
            if y == 0:
                gridNotFull = True
                break
        if gridNotFull:
            break
    
    if not gridNotFull:
        return 0
    return 100

def createMessageEmbed(currentPlayer, playerOneDisplayName, playerTwoDisplayName, color, embedColor, firstLine, selection, grid):
    desc = f'{firstLine}\n\n'
    
    if len(selection) > 0:
        for item in selection:
            desc += f':{getColorSelection(item)}_circle:'
        desc+='\n'

    for row in grid:
        for item in row:
            desc += f':{getColorGrid(item)}_circle:'
        desc += '\n'

    embed = Embed(
        title=f'Connect-4 : {playerOneDisplayName} vs. {playerTwoDisplayName}',
        description=desc,
        color = embedColor
    )

    return embed

async def createMessage(currentPlayer, playerOneDisplayName, playerTwoDisplayName, color, embedColor, firstLine, selection, grid, channel):
    return await channel.send(embed=createMessageEmbed(currentPlayer, playerOneDisplayName, playerTwoDisplayName, color, embedColor, firstLine, selection, grid))

async def updateMessage(currentPlayer, playerOneDisplayName, playerTwoDisplayName, color, embedColor, firstLine, selection, grid, message):
    await message.edit(embed=createMessageEmbed(currentPlayer, playerOneDisplayName, playerTwoDisplayName, color, embedColor, firstLine, selection, grid))

async def playConnectFour(self, playerOne, playerTwo, channel):
    # initialize variables

    if not await confirmation(self, f'<@!{playerTwo.id}>! Do you want to play Connect-Four with {playerOne.display_name}?', playerTwo, channel, cancelledMessage=':x: Connect-Four game cancelled!', successMessage='Starting Connect-Four match'):
        return

    turn = 1
    grid = [[0 for x in range(7)] for y in range(6)] 

    selection = [0, 0, 0, 1, 0, 0, 0]

    playerNumber = 1
    color = 'red'
    currentPlayer = playerOne
    embedColor = Colour.red()

    firstLine = f'<@!{str(currentPlayer.id)}>\'s turn :{color}_circle:'
    new_message = await createMessage(currentPlayer, playerOne.display_name, playerTwo.display_name, color, embedColor, firstLine, selection, grid, channel)

    reaction = None

    await new_message.add_reaction('◀')
    await new_message.add_reaction('▶')
    await new_message.add_reaction('✅')

    while True:
        def check(reaction, user):
            if turn == 1:
                return user == playerOne
            else:
                return user == playerTwo

        if str(reaction) == '◀':
            selection = moveSelection(selection, playerNumber, -1)
        elif str(reaction) == '▶':
            selection = moveSelection(selection, playerNumber, 1)
        elif str(reaction) == '✅':
            if isPlacementPossible(selection, grid):
                grid = updateGrid(selection, grid)
                winner = checkForWinner(selection, grid)

                if winner == 100: # no winner
                    selection = changeSelectionColor(selection)
                    turn = turn * -1
                    
                    if turn == 1:
                        playerNumber = 1
                        color = 'red'
                        currentPlayer = playerOne
                        embedColor = Colour.red()
                    else:
                        playerNumber = 2
                        color = 'yellow'
                        currentPlayer = playerTwo
                        embedColor = Colour.gold()
                else: # Someone won
                    break
        
        firstLine = f'<@!{str(currentPlayer.id)}>\'s turn :{color}_circle:'
        await updateMessage(currentPlayer, playerOne.display_name, playerTwo.display_name, color, embedColor, firstLine, selection, grid, new_message)
            
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout = 60.0, check = check)
            await new_message.remove_reaction(reaction, user)
        except:
            if playerNumber == 1:
                winner = -2
            else:
                winner = -1
            break
        
    await new_message.clear_reactions()
    if winner == 1:
        firstLine = f'**<@!{str(playerOne.id)}> wins!** :red_circle:'
    elif winner == 2:
        firstLine = f'**<@!{str(playerTwo.id)}> wins!** :yellow_circle:'
    elif winner == -1:
        firstLine = f':alarm_clock: Time\'s up! **<@!{str(playerOne.id)}> wins!** :red_circle:'
    elif winner == -2:
        firstLine = f':alarm_clock: Time\'s up! **<@!{str(playerTwo.id)}> wins!** :yellow_circle:'
    elif winner == 0:
        firstLine = f'**No one** wins! We have a tie!'
    else:
        firstLine = f'Error determining winner but the game is over!'

    await updateMessage(currentPlayer, playerOne.display_name, playerTwo.display_name, color, Colour.blue(), firstLine, [], grid, new_message)
# ConnectFour logic END
    
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
        await self.slot_game(interaction, difficulty)

    async def slot_game(self, interaction, difficulty = "normal", contin = False):
        # Money logic
        if (self.economy.get_balance(interaction.user.id) < 100):
            if not contin:
                await interaction.response.send_message("Недостаточно средств! (Необходимо **100$**)", delete_after=10)
            else:
                await interaction.edit_original_response(content="Недостаточно средств! (Необходимо **100$**)", delete_after=10)
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
        if not contin:
            m1 = await interaction.response.send_message(self.render_game(game_matrix)) #, delete_after=game_time+15
        else:
            m1 = await interaction.edit_original_response(content=self.render_game(game_matrix)) #, delete_after=game_time+15
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
        await interaction.edit_original_response(content=f"{self.render_game(game_matrix)}\n───────\nВаш приз: **{prize}$**\n```{prizelog_text}\n```") # , view=Buttons(self.bot, difficulty)
        self.economy.add_money(interaction.user.id, prize)
        
        if (prize<500):
            await asyncio.sleep(5)
            await interaction.delete_original_response()

    @app_commands.command(name = 'cave', description="Cave game (use /cave action:help)")
    async def cave_command(self, interaction, 
                            action: Literal["help", "start (50$)", "end", "status", "feed 🍎 (30$)", "feed 🍞 (60$)", "debug"],
                            target_user: Member = None,
                            ephemeral: bool=False):
        command_id = 1162854751449403529
        str_command = f"</cave:{command_id}>"
        #str_command = "/cave"
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
            help_food_list += f"\n{str_command}`action:{i}` - восстановит **{s['feed']}** ед. голода."
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
Для начала игры используйте {str_command}`action:start (50$)`
Покормить шахтёра {str_command}`action:food <тип_пищи>`
Узнать статус добычи {str_command}`action:status`
Для завершения игры используйте {str_command}`action:end`
Отладочная информация {str_command}`action:debug`
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
Узнать статус игры другого игрока {str_command}`action:status target_user:@пользователь`
Покормить шахтёра другого игрока {str_command}`action:food <тип_пищи> target_user:@пользователь`
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
                    break
                if cave_session is not None:
                    message = "Процесс добычи уже был запущен!"
                    break
                if (self.economy.get_balance(user_id) < 50):
                    message = "Недостаточно средств!"
                    break
                
                self.economy.add_money(user_id, 50*-1)
                self.db.execute("INSERT INTO cave_game (time_start, user_id, hunger) VALUES (?, ?, ?)", [round(time.time()), user_id, max_hunger])
                self.db.commit()
                message = f"## :arrow_forward:Начало добычи\nНе забывайте проверять статус процесса добычи {str_command}` action:status`"
                break
            if (action == "status"):
                if (user_id != target_user_id):
                    title_status = f"**Статус добычи {target_user.display_name}**\n\n"
                else:
                    title_status = f"**Статус добычи** \n\n"
                if cave_session is None:
                    message = f"{title_status}\n**Процесс добычи не запущен!**"
                    break
                    
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

    @app_commands.command(name = "connectfour", description = "play connectfour") 
    async def connectfour_commands(self, interaction, player_two:Member):
        playerOne = interaction.user
        try:
            await interaction.response.send_message('Starting!', ephemeral=True, delete_after=3)
            await playConnectFour(self, playerOne, player_two, interaction.channel)
        except:
            await interaction.response.send_message(':no_entry: Player not found!')


async def setup(bot):
    await bot.add_cog(Minigames(bot))