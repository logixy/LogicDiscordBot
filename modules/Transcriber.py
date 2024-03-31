import io
import speech_recognition
import pydub
import functools
from discord.ext import commands
from discord import app_commands, Embed, Colour, Message, Interaction


class Transcriber(commands.Cog, name="Transcriber"):
    def __init__(self, bot):
        self.bot = bot
        self.previous_transcriptions = {}
        self.trb_embed = Embed(title="✏️ Transcripter", color=Colour.light_embed())

        self.TRANSCRIBE_AUTOMATICALLY = True
        self.TRANSCRIBE_VMS_ONLY = False
        self.TRANSCRIBE_ENGINE = "whisper"


        self.ctx_trcbe = app_commands.ContextMenu(
            name='Transcript',
            callback=self.transcribe_context,
        )
        self.bot.tree.add_command(self.ctx_trcbe)
        

    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def transcribe_context(self, interaction: Interaction, message: Message):
        if message.id in self.previous_transcriptions:
            self.trb_embed.description = self.previous_transcriptions[message.id]
            await interaction.response.send_message(embed=self.trb_embed, ephemeral=True)
            return
        self.trb_embed.description = "Transcription started!"
        await interaction.response.send_message(embed=self.trb_embed, ephemeral=True, delete_after=5)
        await self.transcribe_message(message)

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if self.TRANSCRIBE_AUTOMATICALLY and message.flags.voice and len(message.attachments) == 1:
            await self.transcribe_message(message)

    async def transcribe_message(self, message: Message):
        """Transcribe a message used https://github.com/RyanCheddar/discord-voice-message-transcriber

        Args:
            message (Message): message to transcribe.
        """
        if len(message.attachments) == 0 or not message.attachments[0].content_type.startswith(('audio', 'video')):
            self.trb_embed.description = "Transcription failed! (No Voice)"
            await message.reply(embed=self.trb_embed, mention_author=False)
            return
        if self.TRANSCRIBE_VMS_ONLY and message.attachments[0].content_type != "audio/ogg":
            self.trb_embed.description = "Transcription failed! (Attachment not a Voice Message)"
            await message.reply(embed=self.trb_embed, mention_author=False, delete_after=5)
            return
        
        self.trb_embed.description = "✨ Transcribing..."
        msg = await message.reply(embed=self.trb_embed, mention_author=False)
        try:
            self.previous_transcriptions[message.id] = msg.jump_url
            
            # Read voice file and converts it into something pydub can work with
            voice_file = await message.attachments[0].read()
            voice_file = io.BytesIO(voice_file)
            
            # Convert original .ogg file into a .wav file
            x = await self.bot.loop.run_in_executor(None, pydub.AudioSegment.from_file, voice_file)
            new = io.BytesIO()
            await self.bot.loop.run_in_executor(None, functools.partial(x.export, new, format='wav'))
            
            # Convert .wav file into speech_recognition's AudioFile format or whatever idrk
            recognizer = speech_recognition.Recognizer()
            with speech_recognition.AudioFile(new) as source:
                audio = await self.bot.loop.run_in_executor(None, recognizer.record, source)
            
            # Runs the file through OpenAI Whisper (or API, if configured in config.ini)
            if self.TRANSCRIBE_ENGINE == "whisper":
                result = await self.bot.loop.run_in_executor(None, recognizer.recognize_whisper, audio)
            elif self.TRANSCRIBE_ENGINE == "google":
                result = await self.bot.loop.run_in_executor(None, recognizer.recognize_google, audio)

            if result == "":
                result = "*nothing*"
            # Send results + truncate in case the transcript is longer than 1900 characters
            # self.trb_embed.description = "**Transcription:\n** ```" + result[:4000] + ("..." if len(result) > 4000 else "") + "```"
            # await msg.edit(embed=self.trb_embed)
            chunk_size = 1990  # Set the maximum size of each chunk
            chunks = [result[i:i+chunk_size] for i in range(0, len(result), chunk_size)]
            for i,chunk in enumerate(chunks):
                self.trb_embed.description = chunk
                if i == 0:
                    await msg.edit(embed=self.trb_embed)
                else:
                    self.trb_embed.title = ""
                    await msg.channel.send(embed=self.trb_embed)
        except Exception as e:
            self.trb_embed.description = e.message[:4000]
            await msg.edit(embed=self.trb_embed)


async def setup(bot):
    await bot.add_cog(Transcriber(bot))