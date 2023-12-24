import asyncio
import json
import random
import time
from discord.ext import commands
from discord import app_commands, Embed, Colour, Member, Message
from modules.utils import youchat


class Youchat(commands.Cog, name="Youchat"):
    def __init__(self, bot):
        self.bot = bot
        self.ctx_ai = app_commands.ContextMenu(
            name='AI',
            callback=self.ai_context,
        )
        self.bot.tree.add_command(self.ctx_ai)

    async def youchat_message(self, btext):
        proc = await asyncio.create_subprocess_exec(
                    'python', 'modules/utils/youchat.py', '-t', '12', btext,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        #print(f'[{proc.returncode}]')
        text = json.loads(stdout.decode())
        #print("OUT: " + stdout.decode() + "   " + stderr.decode())
        #print(f'{stderr.decode()}')
        await proc.wait()
        gen_text = text['generated_text']
        gen_text = gen_text.replace('&lt;', '<')
        gen_text = gen_text.replace('&gt;', '>')
        gen_text = gen_text.replace('&le;', '≤')
        gen_text = gen_text.replace('&ge;', '≥')
        gen_text = gen_text.replace('&amp;', '&')
        gen_text = gen_text.replace('&nbsp;', ' ')
        gen_text = gen_text.replace('&quot;', '"')
        gen_text = gen_text.replace('&apos;', "'")
        gen_text = gen_text.replace('&cent;', '¢')
        gen_text = gen_text.replace('&pound;', '£')
        gen_text = gen_text.replace('&yen;', '¥')
        gen_text = gen_text.replace('&euro;', '€')
        gen_text = gen_text.replace('&copy;', '©')
        gen_text = gen_text.replace('&reg;', '®')
        text['generated_text'] = gen_text
        return text
    
    async def chat(self, interaction, message:str, ephemeral: bool=False):
        await interaction.response.send_message('Waiting...', ephemeral=ephemeral)
        attempts = 3
        for i in range(attempts):
            you_chat = asyncio.create_task(self.youchat_message(message))
            you_waiter = asyncio.ensure_future(self.chat_waiter(interaction)) #Waiting...
            
            text = await you_chat
            you_waiter.cancel()# End waiting
            await asyncio.sleep(0.5)
            if 'generated_text' in text and text['generated_text'] != "":
                break;
            elif (i+1 < attempts):
                await interaction.edit_original_response(content=text['error']+f" [Attempt {str(i+2)}/{str(attempts)}]")
                await asyncio.sleep(random.randint(1,3))
                
        if 'generated_text' in text and text['generated_text'] != "":
            gen_text = text['generated_text']
            chunk_size = 1990  # Set the maximum size of each chunk
            chunks = [gen_text[i:i+chunk_size] for i in range(0, len(gen_text), chunk_size)]
            for i,chunk in enumerate(chunks):
                if i == 0:
                    await interaction.edit_original_response(content=chunk)
                else:
                    await interaction.followup.send(chunk, ephemeral=ephemeral)
        else:
            if 'error' in text:
                await interaction.edit_original_response(content=text['error'])
            else:
                await interaction.edit_original_response(content='Request error see the details in the console')
                print(text)

    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name = "chat", description = "Message to GPT chatbot") 
    async def chat_command(self, interaction, message:str, ephemeral: bool=False):
        await self.chat(interaction, message, ephemeral)
    
    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
    async def ai_context(self, interaction, message: Message):
        await self.chat(interaction, message.content, False)

    async def chat_waiter(self, interaction):
        start_dlg = time.time()
        ducks = random.choice([
            ['<:d1:514937588541423617>', '<:d4:803024636099035206>', '<:d2:803024635948040232>', '<:d3:803024636060499988>'],
            ['\N{THINKING FACE}', '<:tf2:802921909539962931>', '<:tf3:802922718810865724>', '<:tf4:1059808410188656771>'],
            ['<:lw_d_p1:970772261319606362><:lw_d_p3:970772260782751826>',
            '<:lw_d_p1:970772261319606362><:lw_d_p2:970772260690493520><:lw_d_p3:970772260782751826>',
            '<:lw_d_p1:970772261319606362><:lw_d_p2:970772260690493520><:lw_d_p2:970772260690493520><:lw_d_p3:970772260782751826>',
            '<:lw_d_p1:970772261319606362><:lw_d_p2:970772260690493520><:lw_d_p2:970772260690493520><:lw_d_p2:970772260690493520><:lw_d_p3:970772260782751826>',
            '<:lw_d_p1:970772261319606362><:lw_d_p2:970772260690493520><:lw_d_p2:970772260690493520><:lw_d_p3:970772260782751826>',
            '<:lw_d_p1:970772261319606362><:lw_d_p2:970772260690493520><:lw_d_p3:970772260782751826>'],
            ['### :regional_indicator_l::regional_indicator_o::regional_indicator_a::regional_indicator_d::regional_indicator_i::regional_indicator_n::regional_indicator_g:',
            '### :regional_indicator_o::regional_indicator_a::regional_indicator_d::regional_indicator_i::regional_indicator_n::regional_indicator_g::hash:',
            '### :regional_indicator_a::regional_indicator_d::regional_indicator_i::regional_indicator_n::regional_indicator_g::hash::hash:',
            '### :regional_indicator_d::regional_indicator_i::regional_indicator_n::regional_indicator_g::hash::hash::hash:',
            '### :regional_indicator_i::regional_indicator_n::regional_indicator_g::hash::hash::hash::hash:',
            '### :regional_indicator_n::regional_indicator_g::hash::hash::hash::hash::hash:',
            '### :regional_indicator_g::hash::hash::hash::hash::hash::hash:',
            '### :hash::hash::hash::hash::hash::hash::hash:',
            '### :hash::hash::hash::hash::hash::hash::regional_indicator_l:',
            '### :hash::hash::hash::hash::hash::regional_indicator_l::regional_indicator_o:',
            '### :hash::hash::hash::hash::regional_indicator_l::regional_indicator_o::regional_indicator_a:',
            '### :hash::hash::hash::regional_indicator_l::regional_indicator_o::regional_indicator_a::regional_indicator_d:',
            '### :hash::hash::regional_indicator_l::regional_indicator_o::regional_indicator_a::regional_indicator_d::regional_indicator_i:',
            '### :hash::regional_indicator_l::regional_indicator_o::regional_indicator_a::regional_indicator_d::regional_indicator_i::regional_indicator_n:'
            ],
            ['### :heart::orange_heart::yellow_heart::green_heart::blue_heart::purple_heart::white_heart:',
            '### :white_heart::heart::orange_heart::yellow_heart::green_heart::blue_heart::purple_heart:',
            '### :purple_heart::white_heart::heart::orange_heart::yellow_heart::green_heart::blue_heart:', 
            '### :blue_heart::purple_heart::white_heart::heart::orange_heart::yellow_heart::green_heart:',
            '### :green_heart::blue_heart::purple_heart::white_heart::heart::orange_heart::yellow_heart:',
            '### :yellow_heart::green_heart::blue_heart::purple_heart::white_heart::heart::orange_heart:',
            '### :orange_heart::yellow_heart::green_heart::blue_heart::purple_heart::white_heart::heart:',
            ],
        ])
        curduck = 0
        while True:
            current_time = time.time()-0.4
            if current_time - start_dlg >= 0.4:
                await interaction.edit_original_response(content=ducks[curduck])
                if (curduck < len(ducks)-1):
                    curduck += 1
                else:
                    curduck = 0
                start_dlg = current_time
                await asyncio.sleep(0.1)
    

async def setup(bot):
    await bot.add_cog(Youchat(bot))