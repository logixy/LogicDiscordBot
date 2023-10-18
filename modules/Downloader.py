import asyncio
import os
import time
import uuid
from discord.ext import commands
from discord import app_commands, Embed, Colour, Member, Message, File
from transliterate import slugify
import yt_dlp
from config import yt_dlp_addr


class Downloader(commands.Cog, name="Downloader"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "dl", description = "Downloader.")
    async def dl_command(self, interaction, name:str, video: bool=False):
        await self.dl_worker(interaction, name, video)

    async def dl_worker(self, interaction, name: str, video: bool):
        start_dl = time.time()
        dl_embed = Embed(title="💾 Downloader", color=Colour.random())
        dl_embed.description = '[1/4] Getting data...'
        await interaction.response.send_message(embed=dl_embed)
        tmp_dir = "tmp"
        r_filename = str(uuid.uuid4())
        ydl_opts = {
            'verbose': True,
            'format': 'bestaudio/best',
            'outtmpl': f"{tmp_dir}/{r_filename}.%(ext)s", # {tmp_dir}/%(title)s.%(ext)s
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
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                loop = asyncio.get_event_loop()
                if (name.startswith("http")):
                    info = await loop.run_in_executor(None, lambda:ydl.extract_info(name, download=False))
                    url = info['webpage_url']
                else:
                    info = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch:{name}", download=False)['entries'][0]) # Search in YouTube
                    url = info['webpage_url']
                d = 1 if 'duration' not in info else info['duration']
                title = info['title']
                ext = 'mp4' if video else 'mp3'
                r_filename = slugify(title)
                if (r_filename is None):
                    r_filename = title.replace(' ', '-')
                file = f"{r_filename}.{ext}"
                path = os.getcwd() + '/' + (tmp_dir+'/'+file).strip()
                dl_embed.description = '[2/4] Checking...'
                await interaction.edit_original_response(embed=dl_embed)
                if d > 1000 and video:
                    raise Exception("Duration (video) longest 1000s")
                if d > 2000:
                    raise Exception("Duration (audio) longest 2000s")
                dl_embed.description = '[3/4] Loading...'
                await interaction.edit_original_response(embed=dl_embed)
                # КостыльGaming inc (multi-threaded ultra asynchronous download)
                if (video):
                    proc = await asyncio.create_subprocess_exec(
                        yt_dlp_addr, '-f', 'b[filesize_approx<=25M] / b[filesize<=25M] / [tbr<600][width<500] / w / bestvideo+bestaudio',
                        '-S', 'res,ext:mp4:m4a', '--recode', ext,
                        '--ignore-errors', '--embed-thumbnail', '--progress', '--newline',
                        '--embed-metadata', '--output', f"{tmp_dir}/{r_filename}.%(ext)s", url,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE)
                else:
                    proc = await asyncio.create_subprocess_exec(
                        yt_dlp_addr, '-x', '--audio-format', 
                        'mp3', '--ignore-errors', '--embed-thumbnail', '--progress', '--newline',
                        '--embed-metadata', '--output', f"{tmp_dir}/{r_filename}.%(ext)s", url,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE)
                        
                start_dlg = time.time()
                while True:
                    line = await proc.stdout.readline()
                    if not line:
                        break
                    current_time = time.time()-1
                    if current_time - start_dlg >= 1:
                        dl_embed.description = '[3/4] '+line.decode().strip()
                        await interaction.edit_original_response(embed=dl_embed)
                        start_dlg = current_time
                    await asyncio.sleep(0.1)
                await proc.wait()
                
                dl_embed.description = '[4/4] Uploading...'
                await interaction.edit_original_response(embed=dl_embed)

                check_file = os.path.exists(path)
                
                if check_file:
                    time_dl = round(time.time() - start_dl, 2)
                    title = f"**{title}**"
                    print("Dl time: "+str(time_dl)+"s")
                    if 'track' in info:
                        title = f"**{info['track']}**"
                    if 'thumbnail' in info:
                        dl_embed.set_thumbnail(url=info['thumbnail'])
                    if 'artist' in info:
                        title += f"\n\n {info['artist']}"
                    elif 'uploader' in info:
                        title += f"\n\n {info['uploader']}"
                    if 'album' in info:
                        title += f" • {info['album']}"
                    if 'album' in info:
                        title += f" • {info['album']}"
                    if 'release_year' in info:
                        title += f" • {info['release_year']}"
                    dl_embed.description = title
                    dl_embed.title = None
                    await interaction.edit_original_response(embed=dl_embed,attachments=[File(path)])
                    os.remove(path)

        except Exception as e:
            e = str(e)
            e = e.replace("\u001b\u005b\u0030\u003b\u0033\u0031\u006d", '**')
            e = e.replace("\u001b\u005b\u0030\u006d", '**')
            e = e.replace("\u001b\u005b\u0030\u003b\u0039\u0034\u006d", '**')
            try:
                os.remove(path)
            finally:
                # Exception pass
                await interaction.edit_original_response(content=e, embed=None)


async def setup(bot):
    await bot.add_cog(Downloader(bot))