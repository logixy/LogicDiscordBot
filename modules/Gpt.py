import asyncio
import time
import g4f
from typing import Literal
from discord.ext import commands
from discord import app_commands, Embed, Colour, Interaction
from modules.utils import webhandler


class Gpt(commands.Cog, name="Gpt"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name = "gpt", description = "GPT command")
    async def gpt_command(self, interaction: Interaction, message: str):
        await interaction.response.send_message("...")
        g4f.debug.logging = True # enable logging
        g4f.check_version = False # Disable automatic version checking
        print(g4f.version) # check version
        print(g4f.Provider.Ails.params)  # supported args

        # Automatic selection of provider

        # streamed completion
        try:
            asyncio.create_task(self.generate_gpt4_response(prompt=message, interaction=interaction))
            #asyncio.ensure_future(self.generate_gpt4_response(prompt=message, interaction=interaction))

            # res = ""
            # time_start = time.time()
            # for message in response:
            #     res += message
            #     if res != "":
            #         if time_start+0.5 > time.time():
            #             time_start = time.time()
            #             await interaction.edit_original_response(content=res)
           # await interaction.edit_original_response(content=response)
        except Exception as e:
            await interaction.edit_original_response(content=str(e))

    async def generate_gpt4_response(self, prompt, interaction):
        try:
            response = await g4f.Provider.Yqcloud.create_async( #  await g4f.ChatCompletion.create.create_async(
                #model="gpt-3.5-turbo",
                model=g4f.models.default.name,
                messages=[{"role": "user", "content": prompt}]
            )
            res = ""
            done = False
            time_start = time.time()
            for message in response:
                res += message
                if res != "":
                    if (time.time() < (time_start+2)):
                        time_start = time.time()
                        await interaction.edit_original_response(content=res[:1999])
            done = True
            if res != "" and done:
                await interaction.edit_original_response(content=res[:1999])
            print( response )
        except Exception as e:
            print("Error: ", e)

async def setup(bot):
    await bot.add_cog(Gpt(bot))