from asyncio import sleep
import asyncio
from discord.ext import commands
from discord import app_commands, Embed, Colour, Member, Message, Interaction, \
                    FFmpegPCMAudio
import yt_dlp


class Playsound(commands.Cog, name="Playsound"):
    def __init__(self, bot):
        self.bot = bot
        self.vc = None

    @app_commands.command(name="play", description="Play sound from url")
    async def play_command(self, interaction: Interaction, name: str):
        p_embed = Embed(title="🎵 Player", color=Colour.random())
        p_embed.description = 'Getting data...'
        await interaction.response.send_message(embed=p_embed)
        ydl_opts = {
            'verbose': True,
            'format': 'bestaudio/best',
            'writethumbnail': True,
            'embedthumbnail': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }, {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            }, { # Embed thumbnail in file 
                'key': 'EmbedThumbnail', 
                'already_have_thumbnail': False, 
            }]
        }
        try:
            # Gets voice channel of message author
            voice_channel = None
            if interaction.user.voice is not None:
                voice_channel = interaction.user.voice.channel
            channel = None
            if voice_channel != None:
                channel = voice_channel.name
                self.vc = await voice_channel.connect()
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    url = None
                    try:
                        loop = asyncio.get_event_loop()
                        if (name.startswith("http")):
                            info = await loop.run_in_executor(None, lambda:ydl.extract_info(name, download=False))
                            url = info['url']
                        else:
                            info = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch:{name}", download=False)['entries'][0]) # Search in YouTube
                            url = info['url']
                    finally:
                        pass
                if url is None:
                    raise Exception('Data is empty!')
                FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
                self.vc.play(FFmpegPCMAudio(url, executable="ffmpeg", **FFMPEG_OPTIONS), after=None)
                # Sleep while audio is playing.
                p_embed.description = f"Playing **{info['title']}** in **{channel}**..."
                await interaction.edit_original_response(embed=p_embed)
                while self.vc.is_playing():
                    await sleep(.1)
                await self.vc.disconnect()
                # Delete command after the audio is done playing.
                await interaction.delete_original_response()
            else:
                p_embed.description = f"{str(interaction.user.display_name)} is not in a voice channel."
                await interaction.edit_original_response(embed=p_embed)
        except Exception as e:
            e = str(e)
            e = e.replace("\u001b\u005b\u0030\u003b\u0033\u0031\u006d", '**')
            e = e.replace("\u001b\u005b\u0030\u006d", '**')
            e = e.replace("\u001b\u005b\u0030\u003b\u0039\u0034\u006d", '**')
            p_embed.description = str(e)
            await interaction.edit_original_response(embed=p_embed)

    @app_commands.command(name="stop", description="Stop audio player")
    async def stop_command(self, interaction: Interaction):
        p_embed = Embed(title="🎵 Player", color=Colour.random())
        if self.vc is not None:
            self.vc.stop()
            p_embed.description = 'Stopped'
        else:
            p_embed.description = 'Player is not connected'
        await interaction.response.send_message(embed=p_embed, delete_after=5)


async def setup(bot):
    await bot.add_cog(Playsound(bot))