"""Purpose: trigger server-specific custom commands when a message starts with the prefix (default "!")."""
import discord
from discord.ext import commands

from src.database import get_connection

PREFIX = "!"

NAME = "on_message"


async def execute(bot: commands.Bot, message: discord.Message):
    if message.author.bot or not message.guild:
        return
    if not message.content.startswith(PREFIX):
        return

    name = message.content[len(PREFIX):].strip().split()[0].lower() if message.content[len(PREFIX):].strip() else None
    if not name:
        return

    conn = get_connection()
    row = conn.execute(
        "SELECT response FROM custom_commands WHERE guild_id = ? AND name = ?",
        (str(message.guild.id), name),
    ).fetchone()
    if not row:
        return

    try:
        await message.channel.send(row["response"])
    except discord.HTTPException:
        pass
