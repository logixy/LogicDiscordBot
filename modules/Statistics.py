import random
from urllib.parse import urlparse
from discord.ext import commands
from discord import app_commands, Embed, Colour, Interaction, Message
from modules.utils import webhandler


class Statistics(commands.Cog, name="Statistics"):
    def __init__(self, bot):
        self.bot = bot
        self.counter_embed = Embed(title="🗳️ Counter", color=Colour.purple())

    @app_commands.command(name="counter", description="Reactions counter")
    async def counter_command(self, interraction: Interaction):
        await interraction.response.send_message('Sending counter...', ephemeral=True, delete_after=1)
        self.counter_embed.description = "waiting for embeds..."
        await interraction.channel.send(embed=self.counter_embed)

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        await self.reactions_update(payload)
    
    @commands.Cog.listener("on_raw_reaction_remove")
    async def on_raw_reaction_remove(self, payload):
        await self.reactions_update(payload)

    async def reactions_update(self, payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        progressbar_size = 12
        if message.embeds.count == 0:
            return
        if len(message.embeds) > 0 and message.embeds[0].title == self.counter_embed.title:
            reactions = ""
            reactions_summ = 0
            for reaction in message.reactions:
                reactions_summ += reaction.count
                
            for reaction in message.reactions:
                progress = round((reaction.count)/(reactions_summ)*100)
                curr_progress_val = progressbar_size*progress//100
                text_progress_bar = ("▰"*curr_progress_val).ljust(progressbar_size, "▱")
                reactions += f"\n {reaction.emoji} {text_progress_bar} {progress}%"
            
            self.counter_embed.description = "waiting for embeds..."
            if reactions != "":
                self.counter_embed.description = reactions
            await message.edit(embed=self.counter_embed)


async def setup(bot):
    await bot.add_cog(Statistics(bot))