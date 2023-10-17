import asyncio
import datetime
import os
import time
from discord.ext import commands
from discord import app_commands, Embed, Colour, Interaction
from typing import Literal
from lib.database import Database

# Main logic

class Core(commands.Cog, name="Core"):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        # Set our error handling function (for timeouts etc)
        bot.tree.on_error = self.on_app_command_error

    @app_commands.checks.cooldown(1, 3, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name = "ping", description = "Ping the bot")
    async def ping_command(self, interaction: Interaction, ephemeral: bool=True):
        await interaction.response.send_message(f"Pong! Latency: {round(self.bot.latency*1000)}ms", ephemeral=ephemeral)

    @app_commands.command(name="dbs", description="Database status")
    async def dbt_command(self, interaction):
        await interaction.response.send_message("Stonks:\n```\n.\n"+self.db.requests_table()+"\n```")

    @app_commands.command(name = "extensions", description = "List of loaded extensions")
    async def extensions_command(self, interaction: Interaction, ephemeral: bool=False):
        title_text = "📃 Modules"
        text = ""
        for filename in os.listdir('./modules'):
            if filename.endswith('.py'):
                text += f"\n**{filename[:-3]}** ["
                loaded = False
                try:
                    await self.bot.load_extension(f'modules.{filename[:-3]}')
                except commands.ExtensionAlreadyLoaded:
                    text += f"**LOADED**"
                    loaded = True
                except commands.ExtensionNotFound:
                    text += f"**ERROR (Not found)**"
                else:
                    text += f"**UNLOADED**"
                    await self.bot.unload_extension(f"modules.{filename[:-3]}")
                text += "]\n "
                if loaded:
                    text += self.get_cog_commands(filename[:-3])   
        embed = Embed(
          title=title_text,
          description=text,
          colour=Colour.green(),
          timestamp=datetime.datetime.now())
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    def get_cog_commands(self, cogname) -> str:
        text = ""
        cog = self.bot.get_cog(cogname)
        for com in cog.get_app_commands():
            text += f"`/{com.name}` "
        for com in cog.get_commands():
            text += f"`{self.bot.command_prefix}{com.name}` "
        return text 

    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name = "extension", description = "Extension Worker")
    async def extension_command(self, interaction: Interaction, extension:str, action: Literal['load', 'unload', 'reload'], ephemeral:bool=False):
        upd = False
        t = ""
        if extension == "*": # For handle all modules
            extensions = os.listdir('./modules')
        else:
            extensions = [f"{extension}.py"]
        for extension in extensions:
            if not extension.endswith(".py"):
                continue
            extension = extension[:-3]
            try:
                if(action == 'load'):
                    await self.bot.load_extension(f'modules.{extension}')
                    t += f"\nExtension **{extension}** - **LOADED**"
                elif(action == 'unload'):
                    if __name__.endswith("."+extension):
                        t += "\nYou can't unload core module!"
                    else:
                        await self.bot.unload_extension(f'modules.{extension}')
                        t += f"\nExtension **{extension}** - **UNLOADED**"
                elif(action == 'reload'):
                    await self.bot.reload_extension(f'modules.{extension}')
                    t += f"\nExtension **{extension}** - **RELOADED**"
                upd = True
                t += "\n Cmds: "+self.get_cog_commands(extension)
            except commands.ExtensionAlreadyLoaded:
                t += f"\n{extension}: **ALREADY LOADED**"
            except commands.ExtensionNotFound:
                t += f"\n{extension}: **ERROR (Not found)**"
            except commands.ExtensionNotLoaded:
                t += f"\n{extension}: **ALREADY UNLOADED**"
        embed = Embed(
          title="🔧 Extension handler",
          description=t,
          colour=Colour.green())
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        if upd:
            synced = await self.bot.tree.sync()
            print(f"[ExtHandler] Synced {len(synced)} command(s).")
            t += f"\nResynced commands complete ({len(synced)} command(s))"
            embed.description = t
            await interaction.edit_original_response(embed=embed)
            await asyncio.sleep(10)
            await interaction.delete_original_response()


    async def on_app_command_error(self, interaction: Interaction, error: app_commands.AppCommandError) -> None:
        mess = ""
        del_time = 10
        if isinstance(error, app_commands.errors.CommandOnCooldown):
            mess = f"{str(error)} (<t:{str(round(time.time()+error.retry_after))}:R>)"
            del_time = error.retry_after
        if isinstance(error, app_commands.errors.MissingPermissions):
            mess = str(error)
        if mess != "":
            await interaction.response.send_message(mess, ephemeral=True, delete_after=del_time)


async def setup(bot):
    await bot.add_cog(Core(bot))