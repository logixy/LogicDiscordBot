from discord.ext import commands
from discord import app_commands, Embed, Colour, Member, Message
from easygoogletranslate import EasyGoogleTranslate


class Translator(commands.Cog, name="Translator"):
    def __init__(self, bot):
        self.bot = bot
        self.tr = EasyGoogleTranslate()
        self.tr_embed = Embed(title="🌐 Translator", color=Colour.blurple())

        self.ctx_tr_ru = app_commands.ContextMenu(
            name='Translate to RU',
            callback=self.translate_ru_context,
        )
        self.bot.tree.add_command(self.ctx_tr_ru)
        
        self.ctx_tr_en = app_commands.ContextMenu(
            name='Translate to EN',
            callback=self.translate_en_context,
        )
        self.bot.tree.add_command(self.ctx_tr_en)

        self.ctx_tr_uk = app_commands.ContextMenu(
            name='Translate to UK',
            callback=self.translate_uk_context,
        )
        self.bot.tree.add_command(self.ctx_tr_uk)

    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name = "translate", description= "Simple translate")
    async def translate_command(self, interaction, text:str, to_lang:str = 'en', from_lang:str = ''):
        translated = self.tr.translate(text, target_language=to_lang, source_language=from_lang)
        self.tr_embed.description = translated
        await interaction.response.send_message(embed=self.tr_embed)
        
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
    async def translate_ru_context(self, interaction, message: Message):
        message.content += self.embeds_text(message)
        translated = self.tr.translate(message.content, target_language='ru')
        self.tr_embed.description = translated
        await interaction.response.send_message(embed=self.tr_embed)
        
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
    async def translate_en_context(self, interaction, message: Message):
        message.content += self.embeds_text(message)
        translated = self.tr.translate(message.content, target_language='en')
        self.tr_embed.description = translated
        await interaction.response.send_message(embed=self.tr_embed)

    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
    async def translate_uk_context(self, interaction, message: Message):
        message.content += self.embeds_text(message)
        translated = self.tr.translate(message.content, target_language='uk')
        self.tr_embed.description = translated
        await interaction.response.send_message(embed=self.tr_embed)

    def embeds_text(self, message: Message):
        text = ""
        if len(message.embeds) > 0:
            for embed in message.embeds:
                text += f"\n**{embed.title}**\n---\n{embed.description}\n"
        return text


async def setup(bot):
    await bot.add_cog(Translator(bot))