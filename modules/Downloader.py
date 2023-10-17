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
        await interaction.response.send_message('[1/5] Getting data...')
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
                if (name.startswith("http")):
                    info = ydl.extract_info(f"{name}", download=False)
                    url = info['webpage_url']
                    d = int(info['duration'])
                else:
                    # Search on ytMusic use ytmAPI
                    #ytm = ytmusicapi.YTMusic()
                    #info = ytm.search(name)[0]
                    #url = f"https://music.youtube.com/watch?v={info['videoId']}"
                    #d = int(info['duration_seconds'])
                    info = ydl.extract_info(f"ytsearch:{name}", download=False)['entries'][0] # Search in YouTube
                    url = info['webpage_url']
                    d = int(info['duration'])
                title = info['title']
                ext = 'mp4' if video else 'mp3'
                r_filename = slugify(title)
                if (r_filename is None):
                    r_filename = title.replace(' ', '-')
                file = f"{r_filename}.{ext}"
                path = os.getcwd() + '/' + (tmp_dir+'/'+file).strip()
                await interaction.edit_original_response(content='[2/5] Checking...')
                if d > 1000 and video:
                    raise Exception("Duration (video) longest 1000s")
                if d > 2000:
                    raise Exception("Duration (audio) longest 2000s")
                await interaction.edit_original_response(content="[3/5] Loading...")
                #ydl.download([url])
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
                #stdout, stderr = await proc.communicate()
                #print(f'[{proc.returncode}]')
                #print(f'{stdout.decode()}')
                #print(f'{stderr.decode()}')
                start_dlg = time.time()
                while True:
                    line = await proc.stdout.readline()
                    if not line:
                        break
                    current_time = time.time()-1
                    if current_time - start_dlg >= 1:
                        await interaction.edit_original_response(content='[3/5] '+line.decode().strip())
                        start_dlg = current_time
                    await asyncio.sleep(0.1)
                await proc.wait()
                
                await interaction.edit_original_response(content='[4/5] Uploading...')

                check_file = os.path.exists(path)
                
                if check_file:
                    await interaction.edit_original_response(content="[5/5] Uploading...")
                    time_dl = round(time.time() - start_dl, 2)
                    title = f"{title} _({str(time_dl)}s)_"
                    await interaction.edit_original_response(content=title,attachments=[File(path)])
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
                await interaction.edit_original_response(content=e)
            
            
    def render_game(gameMatrix) -> str:
        return ''.join(gameMatrix[0]) + \
        "\n" + ''.join(gameMatrix[1]) + \
        "\n" + ''.join(gameMatrix[2])


async def setup(bot):
    await bot.add_cog(Downloader(bot))