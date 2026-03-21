import asyncio
import json
import random
import time
from discord.ext import commands
from discord import app_commands, Embed, Colour, Member, Message, File
from modules.utils import youchat


class Youchat(commands.Cog, name="Youchat"):
    def __init__(self, bot):
        self.bot = bot
        self.ctx_ai = app_commands.ContextMenu(
            name="AI",
            callback=self.ai_context,
        )
        self.bot.tree.add_command(self.ctx_ai)

    async def youchat_message(self, btext):
        proc = await asyncio.create_subprocess_exec(
            "python3",
            "modules/utils/youchat.py",
            "-t",
            "25",
            "-ot",
            "json",
            btext,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        # print(f'[{proc.returncode}]')
        print(stdout.decode())
        text = json.loads(stdout.decode())
        # print("OUT: " + stdout.decode() + "   " + stderr.decode())
        # print(f'{stderr.decode()}')
        await proc.wait()
        gen_text = text["generated_text"]
        gen_text = gen_text.replace("&lt;", "<")
        gen_text = gen_text.replace("&gt;", ">")
        gen_text = gen_text.replace("&le;", "≤")
        gen_text = gen_text.replace("&ge;", "≥")
        gen_text = gen_text.replace("&amp;", "&")
        gen_text = gen_text.replace("&nbsp;", " ")
        gen_text = gen_text.replace("&quot;", '"')
        gen_text = gen_text.replace("&apos;", "'")
        gen_text = gen_text.replace("&cent;", "¢")
        gen_text = gen_text.replace("&pound;", "£")
        gen_text = gen_text.replace("&yen;", "¥")
        gen_text = gen_text.replace("&euro;", "€")
        gen_text = gen_text.replace("&copy;", "©")
        gen_text = gen_text.replace("&reg;", "®")
        gen_text = gen_text.replace("#### ", "### ")
        text["generated_text"] = gen_text
        return text

    async def chat(self, interaction, message: str, ephemeral: bool = False):
        attempts = 3
        for i in range(attempts):
            you_chat = asyncio.create_task(self.youchat_message(message))
            you_waiter = asyncio.ensure_future(
                self.chat_waiter(interaction)
            )  # Waiting...

            text = await you_chat
            you_waiter.cancel()  # End waiting
            await asyncio.sleep(0.5)
            if "generated_text" in text and text["generated_text"] != "":
                break
            elif i + 1 < attempts:
                await interaction.edit_original_response(
                    content=text["error"] + f" [Attempt {str(i+2)}/{str(attempts)}]",
                    attachments=[File("sel.png")],
                )
                await asyncio.sleep(random.randint(1, 3))

        if "generated_text" in text and text["generated_text"] != "":
            await asyncio.sleep(0.1)
            gen_text = text["generated_text"]
            chunk_size = 1990  # Set the maximum size of each chunk
            chunks = [
                gen_text[i : i + chunk_size]
                for i in range(0, len(gen_text), chunk_size)
            ]
            chunks = self.fix_markdown_blocks(chunks)
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await interaction.edit_original_response(
                        content=chunk, attachments=[]
                    )
                else:
                    await interaction.followup.send(chunk, ephemeral=ephemeral)
        else:
            if "error" in text:
                await interaction.edit_original_response(
                    content=text["error"], attachments=[File("sel.png")]
                )
            else:
                await interaction.edit_original_response(
                    content="Request error see the details in the console"
                )
                print(text)

    @commands.Cog.listener("on_message")
    async def chat_message(self, message: Message):
        if message.author.bot or not message.content:
            return

        #await message.channel.send(str(message.mentions[0].id) + " " + str(self.bot.user.id))
        if not message.mentions:
            return

        if message.mentions[0].id in [self.bot.user.id, 473645373408411670, 1232770333296300053]:
            async with message.channel.typing():
                # Обработка сообщения если оно было процитировано
                context = ""
                if message.reference:
                    referenced_message = await message.channel.fetch_message(message.reference.message_id)
                    if isinstance(referenced_message, Message):
                        context = f"Context: \n{referenced_message.content}\n"
                new_content = message.content
                for mention in message.mentions:
                    new_content = new_content.replace(f'<@{mention.id}>', '')  # Удаляем упоминание
                    new_content = f"{context} {message.author.display_name}: \n" + new_content
                you_chat = asyncio.create_task(self.youchat_message(new_content))
                text = await you_chat
                if "generated_text" in text and text["generated_text"] != "":
                    gen_text = text["generated_text"]
                    chunk_size = 1990  # Set the maximum size of each chunk
                    chunks = [
                        gen_text[i : i + chunk_size]
                        for i in range(0, len(gen_text), chunk_size)
                    ]
                    chunks = self.fix_markdown_blocks(chunks)
                    for i, chunk in enumerate(chunks):
                        await message.channel.send(chunk)


    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="chat", description="Message to GPT chatbot")
    async def chat_command(
        self, interaction, message: str, history_cnt: int = 0, ephemeral: bool = False
    ):
        await interaction.response.send_message("Waiting...", ephemeral=ephemeral)
        if history_cnt > 0:
            mess_history = ""
            handled = 0
            async for mess in interaction.channel.history(limit=100):
                if mess.author == interaction.user:
                    mess_history = mess_history + mess.content + "\n"
                    handled += 1
                    # await interaction.edit_original_response(content=handled)
                if handled >= history_cnt:
                    break
            message = mess_history + "\n" + message

        await self.chat(interaction, message, ephemeral)

    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="summary", description="Summary")
    async def s_command(
        self, interaction, msg_count: app_commands.Range[int, 1, 100] = 20
    ):
        await interaction.response.send_message("Handling...")
        messages = []
        try:
            async for message in interaction.channel.history(limit=msg_count):
                # await interaction.edit_original_response(content="mess: "+message.content)
                if not (message.author.bot):
                    messages.append(f"{message.author.display_name}: {message.content}")
        except Exception as e:
            await interaction.edit_original_response(content=e)
        await interaction.edit_original_response(content="end phase #1")
        t = "Напиши краткую сводку диалога не более пяти предложений представленного ниже. Дай свои рекомендации:\n"
        messages = messages[::-1]
        await interaction.edit_original_response(content="start phase #2")
        for message in messages:
            t = t + message + "\n"
        await interaction.edit_original_response(content=f"end phase #2")
        await self.chat(interaction, t, False)

    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
    async def ai_context(self, interaction, message: Message):
        await interaction.response.send_message("Wait a Minute...")
        await self.chat(interaction, message.content, False)

    async def chat_waiter(self, interaction):
        start_dlg = time.time()
        timeout = 50  # repeats
        ducks = random.choice(
            [
                [
                    "<:d1:514937588541423617>",
                    "<:d4:803024636099035206>",
                    "<:d2:803024635948040232>",
                    "<:d3:803024636060499988>",
                ],
                [
                    "\N{THINKING FACE}",
                    "<:tf2:802921909539962931>",
                    "<:tf3:802922718810865724>",
                    "<:tf4:1059808410188656771>",
                ],
                [
                    "<:lw_d_p1:970772261319606362><:lw_d_p3:970772260782751826>",
                    "<:lw_d_p1:970772261319606362><:lw_d_p2:970772260690493520><:lw_d_p3:970772260782751826>",
                    "<:lw_d_p1:970772261319606362><:lw_d_p2:970772260690493520><:lw_d_p2:970772260690493520><:lw_d_p3:970772260782751826>",
                    "<:lw_d_p1:970772261319606362><:lw_d_p2:970772260690493520><:lw_d_p2:970772260690493520><:lw_d_p2:970772260690493520><:lw_d_p3:970772260782751826>",
                    "<:lw_d_p1:970772261319606362><:lw_d_p2:970772260690493520><:lw_d_p2:970772260690493520><:lw_d_p3:970772260782751826>",
                    "<:lw_d_p1:970772261319606362><:lw_d_p2:970772260690493520><:lw_d_p3:970772260782751826>",
                ],
                [
                    "### :regional_indicator_l::regional_indicator_o::regional_indicator_a::regional_indicator_d::regional_indicator_i::regional_indicator_n::regional_indicator_g:",
                    "### :regional_indicator_o::regional_indicator_a::regional_indicator_d::regional_indicator_i::regional_indicator_n::regional_indicator_g::hash:",
                    "### :regional_indicator_a::regional_indicator_d::regional_indicator_i::regional_indicator_n::regional_indicator_g::hash::hash:",
                    "### :regional_indicator_d::regional_indicator_i::regional_indicator_n::regional_indicator_g::hash::hash::hash:",
                    "### :regional_indicator_i::regional_indicator_n::regional_indicator_g::hash::hash::hash::hash:",
                    "### :regional_indicator_n::regional_indicator_g::hash::hash::hash::hash::hash:",
                    "### :regional_indicator_g::hash::hash::hash::hash::hash::hash:",
                    "### :hash::hash::hash::hash::hash::hash::hash:",
                    "### :hash::hash::hash::hash::hash::hash::regional_indicator_l:",
                    "### :hash::hash::hash::hash::hash::regional_indicator_l::regional_indicator_o:",
                    "### :hash::hash::hash::hash::regional_indicator_l::regional_indicator_o::regional_indicator_a:",
                    "### :hash::hash::hash::regional_indicator_l::regional_indicator_o::regional_indicator_a::regional_indicator_d:",
                    "### :hash::hash::regional_indicator_l::regional_indicator_o::regional_indicator_a::regional_indicator_d::regional_indicator_i:",
                    "### :hash::regional_indicator_l::regional_indicator_o::regional_indicator_a::regional_indicator_d::regional_indicator_i::regional_indicator_n:",
                ],
                [
                    "### :heart::orange_heart::yellow_heart::green_heart::blue_heart::purple_heart::white_heart:",
                    "### :white_heart::heart::orange_heart::yellow_heart::green_heart::blue_heart::purple_heart:",
                    "### :purple_heart::white_heart::heart::orange_heart::yellow_heart::green_heart::blue_heart:",
                    "### :blue_heart::purple_heart::white_heart::heart::orange_heart::yellow_heart::green_heart:",
                    "### :green_heart::blue_heart::purple_heart::white_heart::heart::orange_heart::yellow_heart:",
                    "### :yellow_heart::green_heart::blue_heart::purple_heart::white_heart::heart::orange_heart:",
                    "### :orange_heart::yellow_heart::green_heart::blue_heart::purple_heart::white_heart::heart:",
                ],
                ["https://tenor.com/view/hyptonize-frog-gif-11978351"],
                [
                    "<:lw_d_p1:970772261319606362><:lw_d_p2:970772260690493520><:lw_d_p2:970772260690493520><:lw_d_p3:970772260782751826>",
                    "<:lw_d_p2:970772260690493520><:lw_d_p2:970772260690493520><:lw_d_p3:970772260782751826><:lw_d_p1:970772261319606362>",
                    "<:lw_d_p2:970772260690493520><:lw_d_p3:970772260782751826><:lw_d_p1:970772261319606362><:lw_d_p2:970772260690493520>",
                    "<:lw_d_p3:970772260782751826><:lw_d_p1:970772261319606362><:lw_d_p2:970772260690493520><:lw_d_p2:970772260690493520>",
                ],
            ]
        )
        curduck = 0
        loop = 0
        await interaction.edit_original_response(content=ducks[curduck])

        while True:
            current_time = time.time() - 0.4
            if current_time - start_dlg >= 0.4:
                if len(ducks) > 1:
                    await interaction.edit_original_response(content=ducks[curduck])
                if curduck < len(ducks) - 1:
                    curduck += 1
                else:
                    curduck = 0
                    if loop > timeout:
                        break
                    loop += 1
                start_dlg = current_time
                await asyncio.sleep(0.1)

    def fix_markdown_blocks(self, messages):
        fixed_messages = []
        inside_code_block = False  # Флаг, отслеживающий незакрытые блоки кода

        for message in messages:
            lines = message.split("\n")
            open_code_block = False

            for line in lines:
                if line.strip().startswith("```"):
                    open_code_block = not open_code_block  # Переключаем флаг

            if open_code_block:
                if inside_code_block:
                    message = "```\n" + message  # Открываем новый блок
                else:
                    message += "\n```"  # Закрываем текущий блок
                inside_code_block = not inside_code_block

            fixed_messages.append(message)

        return fixed_messages


async def setup(bot):
    await bot.add_cog(Youchat(bot))
