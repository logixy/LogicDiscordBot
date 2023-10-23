import io
import math
import random
import re
from discord.ext import commands
from discord import app_commands, Embed, Colour, Interaction, File
from modules.utils import webhandler


class R34(commands.Cog, name="R34"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 3, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name = "r34", description = "rule34 imgator", nsfw=True)
    async def r34_command(self, interaction: Interaction, tags:str, count:int = 10):
        tags_s = tags.split()
        if 'video' in tags:
            video = True
            if count > 5: count = 5
        else:
            video = False
            # tags_s.append('-video')
            if count > 10: count = 10
        await interaction.response.send_message('[R34] Loading...')
        items_per_page = 100
        # Узнаём сколько всего элементов доступно, и получаем случайную страницу
        await interaction.edit_original_response(content=f"[R34] Random page is...")
        text = webhandler.get_data(f'https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&limit=0&tags={"+".join(tags_s)}')
        count_api = int(re.findall(r'count="([^"]+)"', text)[0])
        if count_api < count: count = count_api # Если доступных изображений меньше чем запрошено к выводу - запоминаем сколько возможно вывести
        count_api_pages = math.ceil(count_api / items_per_page)
        if count_api_pages > 2000: count_api_pages = 2000 # Если страница больше 2000 - api блокируется. тогда жестко закрепляем лимит
        random_page = str(random.randint(1, count_api_pages)-1)
        await interaction.edit_original_response(content=f"Random page is... [{random_page}]")
        text = webhandler.get_data(f'https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&limit={items_per_page}&pid={random_page}&tags={"+".join(tags_s)}')
        urls = re.findall(r'sample_url="([^"]+)"', text)
        if urls:
            if(count > len(urls)):
                urls_random_selected = random.sample(urls, len(urls))# url = random.choice(urls)
            else:
                urls_random_selected = random.sample(urls, count)
                
            formatted_urls = ""
            files = []
            result_size = 0
            max_size = 25000000
            for i,url in enumerate(urls_random_selected):
                if video:
                    formatted_urls += f"[[{i+1}]]({url}) "
                else:
                    resp = webhandler.get(url, timeout=20)
                    await interaction.edit_original_response(content=f"Loading... [{i+1}/{count}] ({round(result_size/1000000, 2)}MB)")
                    file_length = int(resp.headers['Content-Length'])
                    if (file_length+result_size > max_size): continue
                    result_size += file_length
                    data = io.BytesIO(resp.content)
                    file_type = resp.headers['Content-Type'].replace('/', '.')
                    files.append(File(data, str(i)+'_r34.'+file_type))
            await interaction.edit_original_response(content=f"Uploading...")
            try:
                await interaction.edit_original_response(content=f"R34 by tags: **{tags}**\n{formatted_urls}", attachments=files)
            except Exception as e:
                await interaction.edit_original_response(content=e)
        else:
            await interaction.edit_original_response(content='No results found.')

async def setup(bot):
    await bot.add_cog(R34(bot))