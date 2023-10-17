import datetime
from discord.ext import commands
from discord import app_commands, Embed, Colour, Member
from lib.database import Database

class Economy():
    def __init__(self):
        ldb = Database()
        self.db = ldb.db
        self.dbcur = ldb.cursor
        self.dbcur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, user_id VARCHAR(255), money REAL NOT NULL);")
    
    def add_money(self, user, money):
        data = self.db.execute("SELECT user_id FROM users WHERE user_id=?", [user])
        if data.fetchone() != None:
            self.dbcur.execute("UPDATE users SET money=money+? WHERE user_id=?", [money, user])
        else:
            self.dbcur.execute("INSERT INTO users (user_id, money) VALUES (?, ?)", [user, money])
        self.db.commit()

    def get_balance(self, user):
        data = self.db.execute("SELECT money FROM users WHERE user_id=?", [user])
        money_data = data.fetchone()
        if money_data != None:
            return money_data[0]
        else:
            return 0
    
    def get_top_users(self):
        return self.db.execute("SELECT user_id, money FROM users ORDER BY money DESC LIMIT 10")
        
    
class Economics(commands.Cog, name="Economics"):
    def __init__(self, bot):
        self.bot = bot
        self.economy = Economy()

    @app_commands.command(name = "money", description = "Get balance")
    async def money_command(self, interaction, member: Member = None, ephemeral: bool=True):
        if member == None:
            balance = self.economy.get_balance(interaction.user.id)
            mess= f"У вас на счету: **{round(balance, 2)}$**"
        else:
            balance = self.economy.get_balance(member.id)
            mess = f"На счету {member}: **{round(balance, 2)}$**"
        await interaction.response.send_message(mess, ephemeral=ephemeral)

    @app_commands.command(name = "pay", description = "Send money to user")
    async def pay_command(self, interaction, member: Member, money: float, ephemeral: bool=True):
        sender_money = self.economy.get_balance(interaction.user.id)
        if ((sender_money < money) or (money < 0)):
            await interaction.response.send_message(f"У вас недостаточно средств для отправки.", delete_after=10)
            return
        self.economy.add_money(interaction.user.id, money*-1)
        self.economy.add_money(member.id, money)
        await interaction.response.send_message(f"Отправлено **{money}$** пользователю **{member.display_name}**", ephemeral=ephemeral)
        
    @app_commands.command(name = "moneytop", description = "Top Rich")
    async def moneytop_command(self, interaction, ephemeral: bool=True):
        top_text = ""
        for i,row in enumerate(self.economy.get_top_users()):
            top_text += f"**{str(i+1).ljust(2)}**. <@{row[0]}> - **{round(row[1], 2)}$** \n" #{user.display_name}
        embed = Embed(
            title="💰 Топ богачей",
            description=top_text,
            colour=Colour.green(),
            timestamp=datetime.datetime.now())
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        

async def setup(bot):
    await bot.add_cog(Economics(bot))