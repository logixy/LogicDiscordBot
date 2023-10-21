from asyncio import sleep
import asyncio
import time
from discord.ext import commands
from discord import app_commands, Embed, Colour, Member, Message, Interaction, \
                    FFmpegPCMAudio, VoiceState, VoiceClient
import yt_dlp


class Playsound(commands.Cog, name="Playsound"):
    def __init__(self, bot):
        self.bot = bot
        self.vc = {} # {'guild': VoiceClient}
        self.locked = False
        self.queue = {} # {'guild': [queue]}

    @app_commands.command(name="play", description="Play sound from url")
    async def play_command(self, interaction: Interaction, name: str):
        p_embed = Embed(title="🎵 Player", color=Colour.random())
        p_embed.description = 'Getting data...'
        guild_id = interaction.guild.id
        if guild_id not in self.vc:
            await interaction.response.send_message(embed=p_embed)
        else:
            await interaction.response.send_message(embed=p_embed, delete_after=15)
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

            if voice_channel is None:
                p_embed.description = f"{str(interaction.user.display_name)} is not in a voice channel."
                await interaction.edit_original_response(embed=p_embed)
                return

            # Search audio where yt-dlp
            url = None
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Init async loop for use yt-dl functions asynchrony
                loop = asyncio.get_event_loop()
                if (name.startswith("http")):
                    # If audio name is url
                    info = await loop.run_in_executor(None, lambda:ydl.extract_info(name, download=False))
                else:
                    # If audio name is name - search in youtube
                    info = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch:{name}", download=False)['entries'][0]) # Search in YouTube
            if info is None:
                raise Exception('Not found!')
            
            if guild_id not in self.queue:
                self.queue[guild_id] = []
            
            # Add audio to queue
            add_text = ""
            entries = info['entries'] if 'entries' in info else info
            for i in entries:
                self.queue[guild_id].append({'title': i['title'], 
                                            'url': i['url'], 
                                            'thumbnail': i['thumbnail'] if 'thumbnail' in i else "",
                                            'duration': i['duration'] if 'duration' in i else 0})
                add_text += f"➕ {i['title']}\n"
            p_embed.description = add_text + "Added to the queue."
            await interaction.edit_original_response(embed=p_embed)

            if guild_id in self.vc:
                if not self.vc[guild_id].is_connected():
                    self.vc.pop(guild_id)
            if guild_id not in self.vc:
                # channel = voice_channel.name
                self.vc[guild_id] = await voice_channel.connect()
                await self.play(interaction, p_embed)
                await interaction.delete_original_response()
        except Exception as e:
            e = "Error: "+str(e)
            # Replace special chars (colors) in yt-dlp error messages
            e = e.replace("\u001b\u005b\u0030\u003b\u0033\u0031\u006d", '**')
            e = e.replace("\u001b\u005b\u0030\u006d", '**')
            e = e.replace("\u001b\u005b\u0030\u003b\u0039\u0034\u006d", '**')
            p_embed.description = str(e)
            await interaction.edit_original_response(embed=p_embed)

    @app_commands.command(name="stop", description="Stop audio player")
    async def stop_command(self, interaction: Interaction):
        p_embed = Embed(title="🎵 Player", color=Colour.random())
        guild_id = interaction.guild.id
        if guild_id in self.vc:
            self.queue[guild_id] = []
            self.vc[guild_id].stop()
            p_embed.description = 'Stopped'
        else:
            p_embed.description = 'Player is not connected'
        await interaction.response.send_message(embed=p_embed, delete_after=5)
    
    @app_commands.command(name="skip", description="Skip current track")
    async def skip_command(self, interaction: Interaction):
        p_embed = Embed(title="🎵 Player", color=Colour.random())
        guild_id = interaction.guild.id
        if guild_id in self.vc:
            self.vc[guild_id].pause()
            p_embed.description = 'Skipped currently playing track'
        else:
            p_embed.description = 'Player is not connected'
        await interaction.response.send_message(embed=p_embed, delete_after=5)

    @app_commands.command(name="queue", description="Show audio player queue")
    async def queue_command(self, interaction: Interaction):
        p_embed = Embed(title="🎵 Player", color=Colour.random())
        text = ""
        guild_id = interaction.guild.id
        if guild_id in self.queue:
            for i, a in enumerate(self.queue[guild_id]):
                text += f"**{str(i+1)}**. {a['title']}\n"
        if text == "":
            text = "Queue is empty."
        p_embed.description = text
        await interaction.response.send_message(embed=p_embed)
                

    async def play(self, interaction: Interaction, p_embed: Embed):
        guild_id = interaction.guild.id
        if guild_id in self.vc:
            while len(self.queue[guild_id]) > 0:
                sound = self.queue[guild_id].pop(0)
                title = sound['title']
                url = sound['url']
                image = sound['thumbnail']
                start_time = time.time()
                progressbar_size = 13 # Max ▱
                channel = self.vc[guild_id].channel.name
                FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
                self.vc[guild_id].play(FFmpegPCMAudio(url, executable="ffmpeg", **FFMPEG_OPTIONS), after=None)
                curr_text = f"Playing **{title}** in **{channel}**"
                p_embed.description = curr_text
                p_embed.set_thumbnail(url=image)
                await interaction.edit_original_response(embed=p_embed)
                while self.vc[guild_id].is_playing() or self.locked == True:
                    # Draw progress bar ▰▰▰▰▰▰▱▱▱▱▱▱ 50% (if duration is not 0)
                    if sound['duration'] != 0:
                        progress = round((time.time()-start_time)/(sound['duration'])*100)
                        curr_progress_val = progressbar_size*progress//100
                        text_progress_bar = ("▰"*curr_progress_val).ljust(progressbar_size, "▱")
                        p_embed.description = f"{curr_text}\n {text_progress_bar} {progress}%"
                        await interaction.edit_original_response(embed=p_embed)
                    await sleep(1)
            await self.vc[guild_id].disconnect()
            self.vc.pop(guild_id)

    @commands.Cog.listener("on_voice_state_update")
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        if member != self.bot.user:
           return

        vc = member.guild.voice_client
        # Ensure:
        # - this is a channel move as opposed to anything else
        # - this is our instance's voice client and we can action upon it
        if (
            before.channel and  # if this is None this could be a join
            after.channel and  # if this is None this could be a leave
            before.channel != after.channel and  # if these match then this could be e.g. server deafen
            isinstance(vc, VoiceClient) and  # None & not external Protocol check
            vc.channel == after.channel  # our current voice client is in this channel
        ):
            print("Re-connect audio player")
            # If the voice was intentionally paused don't resume it for no reason
            if vc.is_paused():
                return
            # If the voice isn't playing anything there is no sense in trying to resume
            if not vc.is_playing():
                return
            
            await asyncio.sleep(0.5)  # wait a moment for it to set in
            self.locked = True
            vc.pause()
            await asyncio.sleep(0.5)
            vc.resume()
            self.locked = False


async def setup(bot):
    await bot.add_cog(Playsound(bot))