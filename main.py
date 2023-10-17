from discord.ext import commands
import discord
import config as conf
import os

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!lw ", intents=intents)

# Загрузка когов
async def main():
    for filename in os.listdir('./modules'):
        if filename.endswith('.py'):
            await bot.load_extension(f'modules.{filename[:-3]}')

@bot.event
async def on_ready():
    await main()
    print("Success: Bot is connected to Discord")
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s).")


bot.run(conf.bot_token)