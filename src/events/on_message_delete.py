"""Purpose: log deleted messages to the configured log channel."""
import discord
from discord.ext import commands

from src.utils.embeds import COLORS
from src.utils.log_channel import send_log

NAME = "on_message_delete"


async def execute(bot: commands.Bot, message: discord.Message):
    if not message.guild or (message.author and message.author.bot):
        return

    embed = discord.Embed(
        title="🗑️ Message deleted",
        description=message.content or "*No cached content*",
        color=COLORS["warn"],
    )
    embed.add_field(name="Author", value=str(message.author) if message.author else "Unknown", inline=True)
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)

    await send_log(message.guild, embed)
