import base64
import binascii
import hashlib
from typing import Literal

from discord import Embed, Colour, Interaction, app_commands
from discord.ext import commands


def _truncate(s: str, limit: int = 1900) -> str:
    if len(s) <= limit:
        return s
    return s[: limit - 20] + "\n… _(обрезано)_"


class Tech(commands.Cog, name="Tech"):
    """Утилиты: base64, хеши, кодировки."""

    _HASHES = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha224": hashlib.sha224,
        "sha256": hashlib.sha256,
        "sha384": hashlib.sha384,
        "sha512": hashlib.sha512,
        "blake2b": hashlib.blake2b,
        "blake2s": hashlib.blake2s,
    }

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="b64", description="Base64: текст ↔ base64")
    @app_commands.describe(
        direction="encode — текст в base64, decode — base64 в текст",
        text="Исходная строка",
    )
    async def b64_command(
        self,
        interaction: Interaction,
        direction: Literal["encode", "decode"],
        text: str,
    ):
        try:
            if direction == "encode":
                raw = text.encode("utf-8")
                out = base64.b64encode(raw).decode("ascii")
                title = "Base64 (encode)"
            else:
                pad = (-len(text)) % 4
                if pad:
                    text = text + "=" * pad
                raw = base64.b64decode(text, validate=False)
                out = raw.decode("utf-8", errors="replace")
                title = "Base64 (decode)"
        except (binascii.Error, ValueError) as e:
            embed = Embed(
                title="Base64 — ошибка",
                description=f"```\n{e}\n```",
                colour=Colour.red(),
            )
            await interaction.response.send_message(embed=embed)
            return

        embed = Embed(
            title=title,
            description=f"```\n{_truncate(out)}\n```",
            colour=Colour.dark_teal(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="strhash", description="Хеш строки (md5, sha256, …)")
    @app_commands.describe(algorithm="Алгоритм", text="Текст для хеширования")
    @app_commands.choices(
        algorithm=[
            app_commands.Choice(name="MD5", value="md5"),
            app_commands.Choice(name="SHA-1", value="sha1"),
            app_commands.Choice(name="SHA-224", value="sha224"),
            app_commands.Choice(name="SHA-256", value="sha256"),
            app_commands.Choice(name="SHA-384", value="sha384"),
            app_commands.Choice(name="SHA-512", value="sha512"),
            app_commands.Choice(name="BLAKE2b", value="blake2b"),
            app_commands.Choice(name="BLAKE2s", value="blake2s"),
        ]
    )
    async def strhash_command(
        self,
        interaction: Interaction,
        algorithm: str,
        text: str,
    ):
        # discord.py передаёт уже строку value из Choice, не объект Choice
        name = getattr(algorithm, "value", algorithm)
        if name not in self._HASHES:
            await interaction.response.send_message(
                "Неизвестный алгоритм.", ephemeral=True
            )
            return
        h = self._HASHES[name]()
        h.update(text.encode("utf-8"))
        digest = h.hexdigest()
        embed = Embed(
            title=f"Хеш ({name.upper()})",
            description=f"```{digest}```",
            colour=Colour.dark_green(),
        )
        embed.set_footer(text=f"Длина ввода: {len(text)} символов")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="encoding", description="Декодирование: hex, мойабйк, перебор кодировок")
    @app_commands.describe(
        mode="hex — из hex-строки; mojibake — починить кракозябры (UTF-8 прочитан как cp1251 и т.п.); guess — перебор",
        text="Данные (текст или hex)",
        charset="Для mode=hex: целевая кодировка (по умолчанию utf-8)",
    )
    async def encoding_command(
        self,
        interaction: Interaction,
        mode: Literal["hex", "mojibake", "guess"],
        text: str,
        charset: str = "utf-8",
    ):
        if mode == "hex":
            try:
                hex_clean = "".join(text.split())
                if len(hex_clean) % 2:
                    raise ValueError("Нечётное число hex-символов")
                data = bytes.fromhex(hex_clean)
            except ValueError as e:
                embed = Embed(
                    title="Hex — ошибка",
                    description=str(e),
                    colour=Colour.red(),
                )
                await interaction.response.send_message(embed=embed)
                return
            try:
                codec = charset if charset else "utf-8"
                out = data.decode(codec, errors="replace")
            except LookupError:
                embed = Embed(
                    title="Hex — неизвестная кодировка",
                    description=f"`{charset}`",
                    colour=Colour.red(),
                )
                await interaction.response.send_message(embed=embed)
                return
            embed = Embed(
                title=f"Hex → текст ({codec})",
                description=f"```\n{_truncate(out)}\n```",
                colour=Colour.blue(),
            )
            embed.set_footer(text=f"Байт: {len(data)}")
            await interaction.response.send_message(embed=embed)
            return

        if mode == "mojibake":
            # Типичный случай: UTF-8 прочитали как cp1251/latin-1 и т.д.
            pipelines = [
                ("cp1251 → utf-8", lambda s: s.encode("cp1251", errors="strict").decode("utf-8")),
                ("latin-1 → utf-8", lambda s: s.encode("latin-1").decode("utf-8")),
                ("koi8-r → utf-8", lambda s: s.encode("koi8-r", errors="strict").decode("utf-8")),
                ("cp866 → utf-8", lambda s: s.encode("cp866", errors="strict").decode("utf-8")),
                ("iso-8859-5 → utf-8", lambda s: s.encode("iso-8859-5", errors="strict").decode("utf-8")),
            ]
            lines = []
            for label, fn in pipelines:
                try:
                    fixed = fn(text)
                    if fixed and fixed != text:
                        lines.append(f"**{label}**\n{_truncate(fixed, 800)}")
                except (UnicodeDecodeError, UnicodeEncodeError):
                    continue
            if not lines:
                desc = "Подходящих перекодировок не найдено. Попробуйте `mode=guess`."
            else:
                desc = "\n\n".join(lines)
            embed = Embed(
                title="Mojibake (восстановление UTF-8)",
                description=_truncate(desc, 3500),
                colour=Colour.purple(),
            )
            await interaction.response.send_message(embed=embed)
            return

        # guess: байты как latin-1 от строки, затем decode разными кодировками
        try:
            raw = text.encode("latin-1")
        except UnicodeEncodeError:
            embed = Embed(
                title="Guess",
                description="Строка содержит символы вне Latin-1 — используйте hex-режим.",
                colour=Colour.orange(),
            )
            await interaction.response.send_message(embed=embed)
            return

        codecs_try = [
            "utf-8",
            "utf-16-le",
            "utf-16-be",
            "cp1251",
            "koi8-r",
            "cp866",
            "iso-8859-5",
            "mac_cyrillic",
            "latin-1",
        ]
        blocks = []
        for cname in codecs_try:
            try:
                dec = raw.decode(cname, errors="strict")
                preview = _truncate(dec, 500)
                blocks.append(f"**{cname}**\n```{preview}```")
            except UnicodeDecodeError:
                continue
        if not blocks:
            for cname in codecs_try:
                dec = raw.decode(cname, errors="replace")
                preview = _truncate(dec, 500)
                blocks.append(f"**{cname}** _(с заменой ошибок)_\n```{preview}```")
        body = "\n\n".join(blocks[:12])
        embed = Embed(
            title="Перебор кодировок (байты = Latin-1 от ввода)",
            description=_truncate(body, 3800),
            colour=Colour.gold(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Tech(bot))
